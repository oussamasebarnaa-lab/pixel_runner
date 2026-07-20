SCREEN_WIDTH  = 900
SCREEN_HEIGHT = 700
FPS           = 60
TITLE         = "Pixel Runner  |  Pseudo-3D Runner"

VANISHING_POINT_X   = SCREEN_WIDTH  // 2   
VANISHING_POINT_Y   = 185                   
PLAYER_Y            = 575                   

LANE_SPREAD         = 230   
LANE_HORIZON_SPREAD = 18    

MIN_SCALE = 0.05   
MAX_SCALE = 1.00   

SPAWN_DEPTH      = 0.01   
COLLISION_DEPTH  = 0.95   
COLLISION_END    = 1.06   
DESPAWN_DEPTH    = 1.20   

BLACK       = (  0,   0,   0)
WHITE       = (255, 255, 255)

BG_COLOR    = (  6,   6,  18)
ROAD_COLOR  = ( 16,  16,  30)
ROAD_EDGE   = ( 28,  28,  48)
DARK_PANEL  = ( 10,  10,  28)

NEON_BLUE   = (  0, 180, 255)
NEON_GREEN  = (  0, 255, 160)
NEON_PINK   = (255,  20, 160)
NEON_YELLOW = (255, 230,   0)
NEON_ORANGE = (255, 140,   0)
NEON_CYAN   = (  0, 240, 240)
NEON_PURPLE = (160,  30, 255)
GOLD        = (255, 210,   0)
SILVER      = (200, 200, 215)
GRAY        = ( 90,  90, 100)
RED         = (220,  50,  50)

PLAYER_BASE_W = 56    
PLAYER_BASE_H = 88    
PLAYER_ROLL_H = 36    

JUMP_VELOCITY = -17.0   
GRAVITY       =   0.72  

INITIAL_SPEED   = 0.48   
SPEED_INCREMENT = 0.006  
MAX_SPEED       = 1.90

OBS_SPAWN_MIN  = 1.5    
OBS_SPAWN_MAX  = 2.8    
COIN_SPAWN_MIN = 0.8
COIN_SPAWN_MAX = 1.6

SCORE_PER_SECOND = 12   
COIN_VALUE       =  1   

LANE_LEFT   = -0.66
LANE_CENTER =  0
LANE_RIGHT  =  0.66
LANES       = [LANE_LEFT, LANE_CENTER, LANE_RIGHT]

SAVE_FILE = "save_data.json"