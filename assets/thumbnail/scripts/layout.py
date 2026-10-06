"""Rags to Riches thumbnail - shared scene layout (Roblox studs, Z up, camera looks along +Y).

Both the box blockout (blockout.py) and the final scene put each element at the
transform given here, so the composition approved in the blockout carries over.
Box sizes are the bounding boxes of the real models in world_overhaul/blend/.
"""

# Low camera near the ground, wide lens, tilted up so the horizon sits at ~1/5.
CAMERA = dict(loc=(0.0, 0.0, 1.3), pitch=18.0, yaw=-9.0, lens=18.0, sensor=36.0)

# Player (R6, 5.2 studs). yaw: degrees, positive turns his front to the left.
CHARACTER = dict(
    loc=(-2.4, 9.2, 0.0), yaw=-38.0,
    shirt=(0.93, 0.4, 0.1), trousers=(0.16, 0.18, 0.26), skin=(0.96, 0.8, 0.63),
    hair=(0.3, 0.18, 0.1),
)

# Ball and chain: iron ball lying beside him, chain from his left ankle.
BALL = dict(loc=(-5.8, 12.4, 0.0), radius=0.62)

# Foreground pile (debt props) and the credit card debt, right of his feet.
# (name, real-model size, location, yaw)
PILE_SCALE = 0.5   # debt props shrunk so the card reads as a card next to him
PILE = [   # from his right foot spilling right across the bottom of the frame
    ("Debt_CreditCard", (4.4, 1.4, 3.2), (1.2, 10.8, 0.0), 22.0),
    ("Debt_OtherDebt",  (2.3, 2.4, 2.3), (3.6, 11.6, 0.0), 10.0),
    ("Debt_SchoolLoan", (3.3, 3.3, 3.0), (5.6, 13.4, 0.0), -15.0),
    ("Debt_BankLoan",   (3.2, 3.1, 3.2), (7.4, 12.0, 0.0), 30.0),
    ("Bills_a",         (2.6, 1.3, 0.6), (0.4, 9.2, 0.0), 40.0),
    ("Bills_b",         (2.6, 1.3, 0.9), (2.6, 9.6, 0.0), -20.0),
    ("Bills_c",         (2.6, 1.3, 0.5), (4.6, 10.0, 0.0), 75.0),
    ("Bills_d",         (2.6, 1.3, 0.7), (6.2, 10.4, 0.0), -35.0),
    ("Bills_e",         (2.6, 1.3, 0.5), (8.6, 11.0, 0.0), 5.0),
    ("Bills_f",         (2.6, 1.3, 0.6), (5.0, 11.8, 0.6), 50.0),
]

# Dream yacht (real model 11.3 x 42.5 x 14.6, bow +Y) scaled up, floating.
# yaw turns the bow away to the right; bank rolls the deck toward the camera.
YACHT = dict(loc=(80.0, 150.0, 58.0), scale=3.0, yaw=-100.0, bank=40.0, pitch=4.0)   # 40: at 25 the deck stays hidden from this low camera
GLOW = dict(radius=100.0, back=45.0)        # radial glow card behind the yacht

# Middle ground: small, pushed back, left of centre so under the yacht is open sky.
PIZZERIA = dict(name="Workplace_Building_PIZZERIA", size=(49.6, 22.3, 19.5),
                loc=(-12.0, 185.0, 0.0), yaw=22.0, scale=0.85)
PLAZA = dict(loc=(10.0, 150.0, 0.0), radius=11.0)               # Plaza_Disc + fountain
TREES = [(-58.0, 200.0), (-34.0, 160.0), (26.0, 175.0), (48.0, 230.0)]   # Tree 6 x 6 x 14.5
LAMPS = [(-2.0, 125.0), (20.0, 128.0)]                          # Workplace_LampPost 7.9 tall
SHOPS = [((-120.0, 260.0), (9.0, 8.2, 7.0)), ((-28.0, 250.0), (8.0, 8.2, 6.0))]

# Background: tiny hints of other dreams.
SUPERCAR = dict(loc=(150.0, 420.0, 0.0), yaw=70.0)                # 5.4 x 12.2 x 3.3
JET = dict(loc=(-430.0, 900.0, 680.0), yaw=-60.0, roll=-12.0)     # 28.8 x 33 x 12.4
CLOUDS = [(-430.0, 700.0, 300.0, 34.0), (-640.0, 900.0, 600.0, 30.0),
          (980.0, 900.0, 720.0, 40.0)]   # upper left and top-right corner; none under the yacht

# Safe area: nothing important within 8% of any edge.
SAFE = 0.08

# Chains around the yacht. The game lays chain bars on the dream's bounding box; on a
# yacht that turns the silhouette into a box, so here they hug the hull and cabin.
# Yacht-local studs (before YACHT scale): crosswise loops in the XZ plane at a given y,
# and one lengthwise loop round the hull sides at z. Points are padded outward.
CHAIN_PAD = 0.6
CHAIN_LOOPS = [
    ("A", "y", -9.0, [(-3.6, -0.5), (3.6, -0.5), (5.6, 5.5), (4.8, 13.1), (-4.8, 13.1), (-5.6, 5.5)]),
    ("B", "y", 6.0, [(-3.6, -0.5), (3.6, -0.5), (5.6, 5.5), (-5.6, 5.5)]),
    ("C", "z", 3.0, [(-4.8, -19.5), (4.8, -19.5), (4.8, 7.0), (2.8, 13.0), (0.0, 17.5),
                     (-2.8, 13.0), (-4.8, 7.0)]),
]
PADLOCK = dict(local=(5.6, -1.5, 3.0), scale=2.4)   # real Dream_Padlock is 3 x 1.2 x 3.8


# =====================================================================================
# Final scene (step 2): real models, the player's avatar, the two numbers.
# Same camera position and depth layers as the approved blockout.
# =====================================================================================
F_CAMERA = dict(loc=(0.0, 0.0, 1.3), pitch=18.0, yaw=-9.0, roll=6.0, lens=18.0, sensor=36.0)

# The avatar faces the camera, turned `body_turn` deg toward the dream; waist/neck: (x tilt back,
# y side bend, z turn to his left = toward the dream), degrees in his own axes.
F_AVATAR = dict(loc=(-0.55, 8.35, 0.0), body_turn=15.0, waist=(4.0, 0.0, 9.0), neck=(20.0, -4.0, 15.0),
                reach_depth=0.35, reach_min_angle=38.0)

# Ball and chain on his right ankle (screen left), placed beside his feet: offsets in
# camera-aligned ground axes (side: + is screen right, toward: + is toward the camera).
F_BALL = dict(side=-1.75, toward=0.35, radius=0.55)
# The debt number floats just above the ball. cap: height of the digits as a fraction of the
# frame height (0.066 = 9.5 px in a 256x144 thumbnail); dx, dy: screen offset from the ball's top.
F_DEBT_TEXT = dict(text="-$20,000", dx=-0.06, dy=0.08, cap=0.076, tilt=7.0, depth=0.62)
# Debt pile right of his feet: (kind, side, toward, yaw, scale) from his left foot. Cash stacks are
# built with the game's model kit (the game has no cash model); the card is the real Debt_CreditCard.
F_PILE = [
    ("card", 1.0, 1.05, -16.0, 0.42),
    ("cash", 1.75, 0.0, 22.0, 0.44),
    ("cash", 2.45, 0.6, -10.0, 0.46),
    ("cash", 0.55, 0.55, 60.0, 0.4),
    ("cash", 3.15, -0.25, 38.0, 0.44),
]
F_YACHT = dict(loc=(86.0, 150.0, 80.0), scale=3.0, yaw=-100.0, bank=40.0, pitch=4.0)
F_GLOW = dict(radius=118.0, back=50.0, rays=16)
# chain loops on the real hull (yacht-local studs): crosswise at y stations, lengthwise at z
F_CHAINS = dict(cross=(-13.0, -2.0, 8.0), along=(2.6,), link_scale=1.55, pad=0.45, clip_top=11.6)
F_PADLOCK = dict(scale=2.4)
# price tag hanging from the padlock: centre on screen, width as a fraction of the frame width
F_TAG = dict(text="$2,000,000", screen=(0.705, 0.36), width=0.33, aspect=0.25, cap=0.064, swing=-6.0)

F_PIZZERIA = dict(loc=(-6.0, 150.0, 0.0), yaw=200.0, scale=0.8)   # behind him; front (+Y) turned to the camera
F_PLAZA = dict(loc=(14.0, 165.0, 0.0), scale=0.45)
F_TREES = [(-70.0, 175.0, 0.9), (-20.0, 135.0, 0.8), (36.0, 150.0, 0.85), (60.0, 215.0, 1.0),
           (-100.0, 230.0, 1.0)]
F_LAMPS = [(-8.0, 118.0), (22.0, 122.0)]
F_SHOPS = [("Maker_CoffeeShop", (-130.0, 280.0), 15.0), ("Maker_ToyShop", (-6.0, 270.0), -10.0),
           ("Maker_PizzaRestaurant", (90.0, 300.0), -25.0)]
F_SUPERCAR = dict(loc=(185.0, 430.0, 0.0), yaw=70.0)
F_JET = dict(loc=(-430.0, 900.0, 640.0), yaw=-60.0, roll=-12.0)
F_CLOUDS = [(-430.0, 700.0, 300.0, 34.0), (-640.0, 900.0, 600.0, 30.0), (980.0, 900.0, 720.0, 40.0),
            (520.0, 1200.0, 210.0, 46.0)]
# falling coins, real Gold Coin: (screen x, screen y, distance, scale); kept off the tag's text
F_COINS = [(0.54, 0.43, 150, 2.4), (0.585, 0.33, 140, 2.0), (0.93, 0.55, 165, 2.6), (0.88, 0.46, 150, 2.2),
           (0.62, 0.18, 130, 2.0), (0.79, 0.16, 140, 2.3), (0.52, 0.24, 120, 1.7), (0.95, 0.30, 150, 2.0),
           (0.70, 0.08, 110, 1.6), (0.47, 0.57, 160, 1.8)]
# title for the text version: lines (text, cap height), left edge and top on screen, rotation
# icon (512x512): tight on the chained yacht and padlock, his head in the bottom-left corner.
# Raised camera: parallax drops the near head below the far yacht. aim: screen spots for both.
F_ICON = dict(lift=4.0, side=-1.75, lens=32.0, roll=6.0, yacht_at=(0.57, 0.61), res=1024)
F_TITLE = dict(lines=(("CAN YOU", 0.058), ("ESCAPE?", 0.082)), left=0.085, top=0.918, tilt=5.0)
# near coins, rendered on their own layer and blurred: (screen x, screen y, distance, scale, tilt)
F_NEAR = [(0.975, 0.80, 3.0, 0.17, 25.0), (0.03, 0.47, 3.3, 0.16, -35.0), (0.86, 0.035, 2.8, 0.15, 60.0)]
