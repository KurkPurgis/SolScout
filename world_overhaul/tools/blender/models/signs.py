"""
signs.py - the big signs. The TEXT always stays on the old sign part (SurfaceGui), which becomes invisible;
the new board sits 0.06 studs behind the text plane so the text is never hidden or flickering.
"""

import parts


def sign_facing_back(m, center_y, w, h, board, frame, frame_w, depth=0.4, bolts=True):
    """A sign whose text faces +Z (toward the players / camera in the lobby and rooms)."""
    with m.at((0, 0, 0), yaw=180):
        parts.sign_board(m, (0, center_y, 0), w, h, board, frame=frame, frame_w=frame_w, depth=depth,
                         text_plane_z=-0.2, bolts=bolts)


def sign_facing_front(m, center_y, w, h, board, frame, frame_w, depth=0.4, bolts=True):
    parts.sign_board(m, (0, center_y, 0), w, h, board, frame=frame, frame_w=frame_w, depth=depth,
                     text_plane_z=-0.2, bolts=bolts)


MODELS = {
    "Lobby_TitleSign": {"build": lambda m: sign_facing_back(m, 3.5, 68.4, 5.6, "NAVY", "GOLD", 0.7)},
    "AuctionRoom_TitleSign": {"build": lambda m: sign_facing_back(m, 2.0, 29.0, 3.2, "CHARCOAL", "GOLD", 0.45)},
    "AuctionRoom_InfoBoard": {"build": lambda m: sign_facing_back(m, 4.0, 43.0, 7.2, "CHARCOAL", "GOLD", 0.45)},
    "PodiumRoom_TitleSign": {"build": lambda m: sign_facing_back(m, 3.0, 49.0, 5.2, "INK", "GOLD", 0.45)},
    "PodiumRoom_Board": {"build": lambda m: sign_facing_front(m, 9.0, 15.2, 17.2, "INK", "PURPLE", 0.4,
                                                              bolts=False)},
}
