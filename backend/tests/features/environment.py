import asyncio

def before_scenario(context, scenario):
    # Create a new event loop for each scenario
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    context.loop = loop

def after_scenario(context, scenario):
    # Close the event loop after each scenario
    context.loop.close()
    asyncio.set_event_loop(None)