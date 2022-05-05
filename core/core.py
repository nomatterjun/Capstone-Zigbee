import asyncio

async def timeout():
  await asyncio.sleep(4)
  print("Success!")
  
async def main():
  try:
    await asyncio.wait_for(timeout(), timeout=2.0)
  except asyncio.TimeoutError:
    print("Time Out!")
    
asyncio.run(main())
    