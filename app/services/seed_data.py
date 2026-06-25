from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from app.models.prompt_template import PromptTemplate


TEMPLATES = [
    # === Megastructures ===
    {
        "name": "The Last City",
        "description": "A lone human figure stands at the edge of a cliff, gazing at a colossal vertical city that pierces the clouds — every window a world, every spire a nation.",
        "prompt_text": (
            "A vast vertical arcology city rising through multiple layers of atmosphere, brutalist mega-architecture, "
            "a single tiny human silhouette standing on a rocky cliff edge in the foreground, sense of awe and overwhelming scale, "
            "golden hour light piercing through gaps in the structure, volumetric clouds, cinematic composition, "
            "ultra-detailed, photorealistic, 8K, atmospheric haze, lens flare"
        ),
        "category": "megastructure",
        "language": "en",
        "tags": "arcology,brutalist,vertical,city,human-scale,dusk",
    },
    {
        "name": "Orbital Ring",
        "description": "A massive orbital ring encircles the Earth, shuttles like fireflies against the starfield, the planet's curve filling the sky.",
        "prompt_text": (
            "An immense orbital ring megastructure encircling Earth, viewed from a nearby observation platform, "
            "tiny shuttle ships trailing plasma streaks between the ring and the planet surface, "
            "a single astronaut figure standing on the platform edge, the curvature of Earth filling the upper frame, "
            "starfield background, photorealistic, cinematic lighting, ultra-detailed, 8K"
        ),
        "category": "megastructure",
        "language": "en",
        "tags": "orbital,ring,space,earth,astronaut,scale",
    },
    {
        "name": "The Perimeter Wall",
        "description": "A wall so vast it has its own weather system — a tiny caravan of travelers at its base.",
        "prompt_text": (
            "A gargantuan defensive wall stretching beyond the horizon in both directions, so tall its top is shrouded in clouds, "
            "a tiny camel caravan of travelers at the base, sandstorm approaching, the wall disappearing into infinity, "
            "dusty desert atmosphere, cinematic wide shot, photorealistic, 8K, dramatic lighting, scale reference"
        ),
        "category": "megastructure",
        "language": "en",
        "tags": "wall,desert,caravan,infinity,defense,weather",
    },
    {
        "name": "Dyson Swarm Construction",
        "description": "Mirrors the size of continents being positioned around a star, with tiny construction vessels swarming.",
        "prompt_text": (
            "A partially constructed Dyson swarm around a star, continent-sized hexagonal mirror panels being maneuvered into position, "
            "tiny construction ships swarming like insects around each panel, the star's corona flaring through the gaps, "
            "sense of incomprehensible scale, photorealistic, cinematic sci-fi, 8K, volumetric light"
        ),
        "category": "megastructure",
        "language": "en",
        "tags": "dyson-swarm,star,construction,space,scale,mirror",
    },
    {
        "name": "Arcology Interior",
        "description": "The inside of an arcology — habitable levels stacked into the haze of distance, the structure extending beyond sight.",
        "prompt_text": (
            "Interior view of a multi-level arcology megastructure, habitable terraces stacked vertically into the hazy distance, "
            "tiny human figures walking on bridges spanning between building-sized support columns, "
            "the ceiling invisible through atmospheric haze, thousands of lights creating a warm artificial glow, "
            "photorealistic, ultra-detailed, 8K, sense of infinite interior space"
        ),
        "category": "megastructure",
        "language": "en",
        "tags": "arcology,interior,terraces,bridges,scale,lights",
    },

    # === Contrast ===
    {
        "name": "Morning Commute",
        "description": "Tiny figures cross a glass bridge suspended inside a room the size of a processor core, on their way to work.",
        "prompt_text": (
            "A massive industrial interior space resembling a computer processor core, with towering silicon-like structures and copper pathways, "
            "a glass bridge suspended across the vast chasm with tiny human commuters crossing it like ants, "
            "warm morning light streaming through a distant opening, the scale contrast between the microscopic figures and the architectural enormity, "
            "photorealistic, 8K, cinematic, ray tracing reflections"
        ),
        "category": "contrast",
        "language": "en",
        "tags": "commute,industrial,bridge,processor,glass,ant-like",
    },
    {
        "name": "The Library",
        "description": "A library where each bookshelf is a skyscraper — a lone scholar on a floating platform browses the spines.",
        "prompt_text": (
            "A library of cosmic scale where each bookshelf is the height of a skyscraper, "
            "a single tiny scholar on a floating platform hovering before the massive book spines, "
            "warm amber lighting, dust motes dancing in light beams, gothic architecture fused with cyberpunk, "
            "photorealistic, ultra-detailed, 8K, dramatic scale contrast"
        ),
        "category": "contrast",
        "language": "en",
        "tags": "library,bookshelf,scholar,gothic,cyberpunk,floating",
    },
    {
        "name": "最后的守望者",
        "description": "一个渺小的人影站在巨型机械结构的边缘，脚下是无尽的齿轮深渊。",
        "prompt_text": (
            "一个渺小的人类身影站在一座巨型机械结构的边缘，脚下是深不见底的齿轮深渊，"
            "巨型齿轮和活塞在缓慢运转，蒸汽弥漫，金色的光芒从结构深处透出，"
            "电影级构图，写实风格，超高细节，8K，壮丽的尺度对比，氛围感"
        ),
        "category": "contrast",
        "language": "zh",
        "tags": "机械,齿轮,深渊,蒸汽,守望着,中文",
    },
    {
        "name": "Pilgrim's Path",
        "description": "A line of pilgrims walking across a bridge suspended between two megastructure towers, the drop below fading into mist.",
        "prompt_text": (
            "A thin bridge suspended between two colossal futuristic megastructure towers, a line of tiny pilgrims in flowing robes walking across, "
            "the drop below vanishing into white mist, the towers stretching beyond the frame both upward and downward, "
            "ethereal morning light, photorealistic, vertical composition, 8K, sense of spiritual journey and vast scale"
        ),
        "category": "contrast",
        "language": "en",
        "tags": "bridge,pilgrims,towers,mist,spiritual,vertical",
    },

    # === Post-Human ===
    {
        "name": "Gardens of the Forgotten",
        "description": "An overgrown megastructure reclaimed by nature — moss, vines, and towering trees where once there were machines.",
        "prompt_text": (
            "A colossal abandoned megastructure now overgrown with lush vegetation, massive tree roots cracking through ancient metal floors, "
            "vines hanging from impossibly high ceilings, bioluminescent fungi glowing in the shadows, "
            "no human figures — nature has reclaimed the titan architecture, post-human solarpunk aesthetic, "
            "photorealistic, 8K, atmospheric ray-traced lighting, serene and melancholic"
        ),
        "category": "post_human",
        "language": "en",
        "tags": "overgrown,nature,reclaimed,solarpunk,bioluminescence,abandoned",
    },
    {
        "name": "The Silent Forge",
        "description": "A fully automated factory complex the size of a mountain range, still operating centuries after its makers vanished.",
        "prompt_text": (
            "An endless fully automated factory complex stretching across a mountain range, robotic arms the size of buildings still working, "
            "no human presence anywhere — the machines have outlived their creators, sparks and molten metal illuminating the dark facility, "
            "post-human industrial aesthetic, photorealistic, ultra-wide composition, 8K, haunting beauty"
        ),
        "category": "post_human",
        "language": "en",
        "tags": "factory,automated,abandoned,robots,post-human,industrial",
    },
    {
        "name": "Echo Chamber",
        "description": "A vast empty hall within a megastructure — every sound echoes for minutes, and no one has walked here in millennia.",
        "prompt_text": (
            "An immense empty hall inside an ancient alien megastructure, polished obsidian floor reflecting dim glowing runes on distant walls, "
            "no living beings present, dust settled on everything, the hall stretches so far the far wall is barely visible, "
            "eerie blue ambient light from unknown sources, photorealistic, 8K, profound silence and cosmic loneliness"
        ),
        "category": "post_human",
        "language": "en",
        "tags": "empty,hall,alien,obsidian,runes,loneliness",
    },

    # === Interior ===
    {
        "name": "Engine Heart",
        "description": "Inside a Dyson sphere's power core — glowing plasma conduits the size of planets, with tiny maintenance drones for scale.",
        "prompt_text": (
            "Interior of a Dyson sphere's central power core, planet-sized glowing plasma conduits snaking through the vast chamber, "
            "tiny maintenance drones like specks of dust floating near the conduits, blue-white plasma light illuminating everything, "
            "the engineering is so vast it becomes indistinguishable from cosmic phenomena, photorealistic, 8K, volumetric rays"
        ),
        "category": "interior",
        "language": "en",
        "tags": "dyson-sphere,plasma,engine,conduits,drones,power",
    },
    {
        "name": "Water Treatment",
        "description": "An arcology's water purification chamber — waterfalls inside buildings inside cathedrals of industry.",
        "prompt_text": (
            "A cathedral-like water treatment facility inside an arcology, massive waterfalls cascading between architectural levels, "
            "tiny worker figures on observation platforms between the falls, rainbows forming in the mist, "
            "the blend of industrial function and sacred architecture, photorealistic, 8K, dramatic lighting, prismatic light"
        ),
        "category": "interior",
        "language": "en",
        "tags": "waterfall,cathedral,industrial,arcology,rainbow,water",
    },
    {
        "name": "Data Cathedral",
        "description": "Holographic data streams in a space so vast that servers form geological layers — a lone technician on a platform.",
        "prompt_text": (
            "A vast data center cathedral where server stacks form geological strata rising into darkness, "
            "holographic data streams flowing between the racks like rivers of light, "
            "a single tiny technician standing on a floating maintenance platform, "
            "the fusion of medieval cathedral architecture with quantum computing infrastructure, "
            "photorealistic, 8K, cyberpunk-gothic, atmospheric lighting"
        ),
        "category": "interior",
        "language": "en",
        "tags": "data-center,cathedral,holographic,quantum,gothic,technician",
    },
    {
        "name": "The Hangar",
        "description": "A spacecraft hangar within a megastructure — ships like cruise liners, each one a speck against the ceiling.",
        "prompt_text": (
            "An impossibly large spacecraft hangar inside an orbital megastructure, ships the size of ocean liners docked in rows, "
            "tiny ground crew figures and service vehicles on the deck, the hangar ceiling is so high it fades into atmospheric haze, "
            "massive holographic displays showing ship schedules, photorealistic, 8K, cinematic, industrial sci-fi"
        ),
        "category": "interior",
        "language": "en",
        "tags": "hangar,spaceship,orbital,docked,ground-crew,sci-fi",
    },

    # === Landscape ===
    {
        "name": "Desert Spire",
        "description": "A single vertical city-spire standing alone in an endless desert — tiny travelers approach from the horizon.",
        "prompt_text": (
            "A single impossibly tall vertical city-spire rising from an endless golden desert, the only structure in a sea of sand dunes, "
            "a tiny caravan of travelers approaching from the far horizon, their trail stretching back into the distance, "
            "the spire's shadow stretches for miles across the desert, sunset golden hour, "
            "photorealistic, 8K, cinematic wide shot, sense of isolation and awe"
        ),
        "category": "landscape",
        "language": "en",
        "tags": "spire,desert,caravan,isolation,sunset,sand",
    },
    {
        "name": "Floating Citadel",
        "description": "A floating city drifts above a misty ocean — fishing boats below, each one dwarfed by the shadow above.",
        "prompt_text": (
            "A massive floating citadel hovering above a mist-covered ocean, its shadow darkening the sea below, "
            "tiny fishing boats on the water beneath the structure, waterfalls cascading from the floating city into the ocean, "
            "the contrast between the ancient wooden boats and the futuristic floating architecture, "
            "photorealistic, 8K, atmospheric mist, cinematic composition, vertical scale"
        ),
        "category": "landscape",
        "language": "en",
        "tags": "floating,citadel,ocean,boats,waterfall,mist",
    },
    {
        "name": "峡谷巨门",
        "description": "在两座巨山之间嵌着一扇巨门，门缝中渗透出光芒，山脚下的人群如同尘埃。",
        "prompt_text": (
            "在两座巍峨巨山之间嵌着一扇巨大的未来主义风格大门，门缝中渗透出温暖的金色光芒，"
            "山脚下有微小如尘埃的人群聚集，仰望着这扇巨门，峡谷中的雾气弥漫，"
            "电影级构图，写实风格，超高细节，8K，神秘的史诗氛围，垂直尺度对比"
        ),
        "category": "landscape",
        "language": "zh",
        "tags": "峡谷,巨门,光芒,神秘,史诗,中文",
    },
    {
        "name": "Bridge Between Worlds",
        "description": "A bridge spanning two continental plates — small towns have been built along its guardrails over centuries.",
        "prompt_text": (
            "A megastructure bridge spanning between two continental plates across a vast ocean, so wide that small towns and villages "
            "have been built along its guardrails over centuries, tiny ships passing underneath through arched pillars the size of mountains, "
            "the bridge extends to the vanishing point of the horizon, golden sunset light, "
            "photorealistic, 8K, ultra-wide panorama, the scale of infrastructure beyond comprehension"
        ),
        "category": "landscape",
        "language": "en",
        "tags": "bridge,continental,towns,ocean,sunset,infrastructure",
    },

    # === More Megastructures ===
    {
        "name": "Starscraper Foundation",
        "description": "The foundation of a building so vast it has tectonic plates — workers in exosuits on the excavation floor.",
        "prompt_text": (
            "The foundation pit of a starscraper megastructure, so vast it exposes geological layers and tectonic plates, "
            "tiny workers in illuminated exosuits working on the excavation floor far below, massive support columns being erected, "
            "the scale is geological rather than architectural, photorealistic, 8K, dramatic industrial lighting, depth and scale"
        ),
        "category": "megastructure",
        "language": "en",
        "tags": "foundation,excavation,tectonic,exosuit,geological,construction",
    },
    {
        "name": "The Sprawl at Night",
        "description": "A sprawling mega-city seen from a mountain at night — a galaxy of lights stretching to the curved horizon.",
        "prompt_text": (
            "A sprawling megacity seen from a dark mountain peak at night, the city lights spreading like a galaxy to the curved horizon, "
            "a tiny human figure sitting on the mountain ledge looking down at the endless urban expanse, "
            "neon glow, light pollution haze, the city is so vast it becomes an abstract canvas of light, "
            "photorealistic, 8K, cinematic night photography, profound isolation within urban immensity"
        ),
        "category": "megastructure",
        "language": "en",
        "tags": "sprawl,city,night,lights,mountain,urban",
    },
]

TEMPLATES_ZH = [
    {
        "name": "无尽阶梯",
        "description": "一道通向天际的阶梯，每一级台阶都如广场般宽阔，人们如同蚂蚁般攀登。",
        "prompt_text": (
            "一道通向天际的巨型阶梯，每一级台阶都如城市广场般宽阔，微小的人群如同蚂蚁在台阶上攀登，"
            "阶梯两侧是云雾缭绕的深渊，顶端消失在云层之中，金色的阳光从顶部洒下，"
            "电影级构图，写实风格，超高细节，8K，壮丽的尺度感，巴洛克风格装饰"
        ),
        "category": "megastructure",
        "language": "zh",
        "tags": "阶梯,天际,攀登,云雾,巴洛克,中文",
    },
    {
        "name": "铸造星辰",
        "description": "一座恒星锻造厂——巨型机械臂正在组装一颗人造太阳，工人们只是光点中的光点。",
        "prompt_text": (
            "一座环绕恒星的巨型工业锻造厂，巨大的机械臂正在组装一颗人造太阳，等离子体在空间中流淌，"
            "微小的工人身影在机械臂上行走，相比之下如尘埃般渺小，炽热的橙色和蓝色光芒交织，"
            "科幻工业美学，写实风格，超高细节，8K，宇宙尺度的震撼"
        ),
        "category": "megastructure",
        "language": "zh",
        "tags": "恒星,锻造,机械臂,等离子,工业,中文",
    },
]


async def seed_templates(session_factory: async_sessionmaker[AsyncSession]) -> None:
    """Seed the database with curated prompt templates if none exist."""
    async with session_factory() as session:
        result = await session.execute(select(func.count()).select_from(PromptTemplate))
        count = result.scalar()

        if count > 0:
            return  # Already seeded

        for t in TEMPLATES + TEMPLATES_ZH:
            template = PromptTemplate(
                name=t["name"],
                description=t["description"],
                prompt_text=t["prompt_text"],
                category=t["category"],
                language=t["language"],
                tags=t.get("tags", ""),
                is_builtin=True,
            )
            session.add(template)

        await session.commit()
