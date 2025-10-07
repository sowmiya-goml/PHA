"""Bedrock-powered chatbot using MCP tools."""

import boto3
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from core.config import settings
import anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class BedrockMCPChatbot:
    """Chatbot powered by AWS Bedrock using MCP tools."""
    
    def __init__(self):
        """Initialize Bedrock chatbot with MCP client."""
        self.bedrock_client = boto3.client(
            'bedrock-runtime',
            region_name=settings.AWS_DEFAULT_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        self.model_id = settings.BEDROCK_MODEL_ID
        self.conversation_history: List[Dict[str, Any]] = []
        self.mcp_session: Optional[ClientSession] = None
        self.available_tools: List[Dict[str, Any]] = []
        self._read = None
        self._write = None
        self._stdio_context = None
        self._session_context = None
    
    async def initialize_mcp(self):
        """Initialize MCP client connection."""
        # Get the absolute path to mcp_server.py
        current_dir = os.path.dirname(os.path.abspath(__file__))
        mcp_server_path = os.path.join(current_dir, "mcp_server.py")
        
        server_params = StdioServerParameters(
            command="python",
            args=[mcp_server_path],
            env=None
        )
        
        # Keep the context managers alive
        self._stdio_context = stdio_client(server_params)
        self._read, self._write = await self._stdio_context.__aenter__()
        
        self._session_context = ClientSession(self._read, self._write)
        self.mcp_session = await self._session_context.__aenter__()
        
        await self.mcp_session.initialize()
        
        # Get available tools
        tools_result = await self.mcp_session.list_tools()
        self.available_tools = [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema
            }
            for tool in tools_result.tools
        ]
    
    async def chat(
        self,
        user_message: str,
        connection_id: str,
        patient_id: Optional[str] = None,
        max_iterations: int = 5
    ) -> Dict[str, Any]:
        """
        Process user message and generate response using Bedrock and MCP tools.
        
        Args:
            user_message: User's query
            connection_id: Database connection ID
            patient_id: Optional patient ID
            max_iterations: Maximum tool calling iterations
            
        Returns:
            Response with answer and metadata
        """
        try:
            # Add user message to conversation
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })
            
            # Build system prompt with available tools
            system_prompt = self._build_system_prompt(connection_id, patient_id)
            
            iteration = 0
            tool_results = []
            all_tools_used = []
            
            while iteration < max_iterations:
                iteration += 1
                
                # Call Bedrock Claude with tool definitions
                response = await self._call_bedrock_with_tools(
                    system_prompt=system_prompt,
                    messages=self.conversation_history,
                    tools=self._convert_tools_to_bedrock_format()
                )
                
                # Check if Claude wants to use tools
                if response.get("stop_reason") == "tool_use":
                    # Extract tool calls
                    tool_use_blocks = [
                        block for block in response.get("content", [])
                        if block.get("type") == "tool_use"
                    ]
                    
                    if not tool_use_blocks:
                        break
                    
                    # Execute tools via MCP
                    tool_results, tool_names = await self._execute_mcp_tools(tool_use_blocks)
                    all_tools_used.extend(tool_names)
                    
                    # Add assistant response and tool results to conversation
                    self.conversation_history.append({
                        "role": "assistant",
                        "content": response.get("content", [])
                    })
                    
                    self.conversation_history.append({
                        "role": "user",
                        "content": tool_results
                    })
                    
                else:
                    # No more tools to call, extract final answer
                    assistant_message = self._extract_text_from_response(response)
                    
                    self.conversation_history.append({
                        "role": "assistant",
                        "content": assistant_message
                    })
                    
                    return {
                        "status": "success",
                        "answer": assistant_message,
                        "tools_used": all_tools_used,
                        "iterations": iteration,
                        "timestamp": datetime.now().isoformat()
                    }
            
            # Max iterations reached
            return {
                "status": "partial",
                "answer": "I need more iterations to complete this request.",
                "tools_used": all_tools_used,
                "iterations": iteration,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            import traceback
            error_msg = f"{str(e)}\n\nTraceback:\n{traceback.format_exc()}"
            print(f"Chat error: {error_msg}")
            return {
                "status": "error",
                "answer": error_msg,
                "error": str(e),
                "tools_used": [],
                "iterations": 0,
                "timestamp": datetime.now().isoformat()
            }
    
    def _build_system_prompt(self, connection_id: str, patient_id: Optional[str]) -> str:
        """Build system prompt with context."""
        return f"""You are a helpful healthcare assistant with access to patient data through specialized tools.

Current Context:
- Database Connection ID: {connection_id}
- Patient ID: {patient_id if patient_id else "Not specified"}

Your capabilities:
- Access patient demographics, medications, conditions, lab results, procedures, allergies, appointments, diet info, and vital signs
- Provide comprehensive health information
- Answer questions about patient care

Guidelines:
1. Use tools to fetch real data from the database
2. Always use the provided connection_id and patient_id when calling tools
3. Provide clear, accurate, and helpful responses
4. If you need a patient_id and it's not provided, ask the user for it
5. Present information in a clear, organized manner
6. Cite which tools you used to get the information

Available tools: {', '.join([tool['name'] for tool in self.available_tools])}
"""
    
    async def _call_bedrock_with_tools(
        self,
        system_prompt: str,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Call Bedrock Claude with tool definitions."""
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4000,
            "temperature": 0.1,
            "system": system_prompt,
            "messages": messages,
            "tools": tools
        }
        
        response = self.bedrock_client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(body),
            contentType='application/json'
        )
        
        return json.loads(response['body'].read().decode())
    
    def _convert_tools_to_bedrock_format(self) -> List[Dict[str, Any]]:
        """Convert MCP tools to Bedrock/Claude tool format."""
        return [
            {
                "name": tool["name"],
                "description": tool["description"],
                "input_schema": tool["input_schema"]
            }
            for tool in self.available_tools
        ]
    
    async def _execute_mcp_tools(
        self,
        tool_use_blocks: List[Dict[str, Any]]
    ) -> tuple[List[Dict[str, Any]], List[str]]:
        """Execute tools via MCP. Returns (results, tool_names)."""
        results = []
        tool_names = []
        
        for tool_block in tool_use_blocks:
            tool_name = tool_block.get("name")
            tool_input = tool_block.get("input", {})
            tool_use_id = tool_block.get("id")
            tool_names.append(tool_name)
            
            try:
                # Call MCP tool
                result = await self.mcp_session.call_tool(tool_name, tool_input)
                
                # Extract content from MCP result
                if hasattr(result, 'content'):
                    # result.content is a list of content blocks from MCP
                    content_blocks = result.content
                    if content_blocks and len(content_blocks) > 0:
                        # Get the first content block (usually contains the data)
                        first_block = content_blocks[0]
                        if hasattr(first_block, 'text'):
                            tool_content = first_block.text
                        else:
                            tool_content = json.dumps(first_block) if not isinstance(first_block, str) else first_block
                    else:
                        tool_content = json.dumps(content_blocks)
                else:
                    tool_content = str(result)
                
                results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_use_id,
                    "content": tool_content
                })
                
            except Exception as e:
                error_msg = f"Error executing tool {tool_name}: {str(e)}"
                print(f"MCP tool error: {error_msg}")
                results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_use_id,
                    "content": error_msg,
                    "is_error": True
                })
        
        return results, tool_names
    
    def _extract_text_from_response(self, response: Dict[str, Any]) -> str:
        """Extract text content from Bedrock response."""
        content = response.get("content", [])
        text_blocks = [
            block.get("text", "")
            for block in content
            if block.get("type") == "text"
        ]
        return "\n".join(text_blocks)
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get conversation history."""
        return self.conversation_history
    
    async def cleanup(self):
        """Clean up MCP session resources."""
        try:
            # Close in reverse order of opening
            if self._session_context and self.mcp_session:
                try:
                    await self._session_context.__aexit__(None, None, None)
                except RuntimeError as e:
                    # Ignore "different task" errors during cleanup
                    if "different task" not in str(e):
                        raise
                except Exception as e:
                    print(f"Error closing session context: {e}")
                finally:
                    self.mcp_session = None
                    self._session_context = None
            
            if self._stdio_context:
                try:
                    await self._stdio_context.__aexit__(None, None, None)
                except RuntimeError as e:
                    # Ignore "different task" errors during cleanup
                    if "different task" not in str(e):
                        raise
                except Exception as e:
                    print(f"Error closing stdio context: {e}")
                finally:
                    self._stdio_context = None
                    self._read = None
                    self._write = None
        except Exception as e:
            print(f"Error during MCP cleanup: {e}")