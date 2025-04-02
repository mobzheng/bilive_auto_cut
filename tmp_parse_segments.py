import asyncio

import threading


def _start_thread(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


async def main():
    await asyncio.sleep(2)
    print("Hello World!")


loop = asyncio.new_event_loop()
t = threading.Thread(target=_start_thread, args=(loop,))
t.daemon = True
t.start()

c1 = main()
c2 = main()
c3 = main()
c4 = main()
asyncio.run_coroutine_threadsafe(c1, loop)
asyncio.run_coroutine_threadsafe(c2, loop)
asyncio.run_coroutine_threadsafe(c3, loop)
asyncio.run_coroutine_threadsafe(c4, loop)
t.join()