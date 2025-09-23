from utils.aws import call_bedrock_summary

async def chunk(data,prompt_fn):
    chunk_size = len(data) // 3
    remainder = len(data) % 3
    chunks = []
    start = 0
    # print(data, chunk_size, remainder)
    for i in range(3):
        end = start + chunk_size + (1 if i < remainder else 0)
        chunks.append(data[start:end])
        start = end
    # print("****chunks****",chunks)
    summary = ""
    for idx, chunk in enumerate(chunks):
        prompt = prompt_fn(chunk)
        partial_summary = call_bedrock_summary(prompt) 
        chunk_summary = ""
        async for part in partial_summary.body_iterator:
            chunk_summary += part

        summary += chunk_summary
    return summary