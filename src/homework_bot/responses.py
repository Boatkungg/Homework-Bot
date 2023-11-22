from discord import ApplicationContext, Embed


async def normal_response(
    ctx: ApplicationContext, message: str, color=Embed.Empty, **kwargs
):
    embed = Embed(color=color)
    embed.description = message
    await ctx.respond(embed=embed, **kwargs)
