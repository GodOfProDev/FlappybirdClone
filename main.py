import pygame, sys, random, json, time, os, button
from cryptography.fernet import Fernet
from threading import Thread
from time import sleep

key = "FuGxRMgLoA_lW62jYKpWoW0ieYUBMaryvlAOqp-aQpY="
f = Fernet(key)

def crypt_file():
    with open("score.txt", "rb") as original_file:
        original = original_file.read()

    encrypted = f.encrypt(original)

    with open("enc_score.txt", "wb") as encrypted_file:
        encrypted_file.write(encrypted)

def decrypt_file():
    with open("enc_score.txt", "rb") as encrypted_file:
        encrypted = encrypted_file.read()

    decrypted = f.decrypt(encrypted)

    with open("score.txt", "wb") as decrypted_file:
        decrypted_file.write(decrypted)

def draw_floor():
    screen.blit(floor_surface,(floor_x_pos,570))
    screen.blit(floor_surface,(floor_x_pos + 400,570))

def create_pipe():
    random_pipe_pos = random.choice(pipe_height)
    bottom_pipe = pipe_surface.get_rect(midtop = (500,random_pipe_pos))
    top_pipe = pipe_surface.get_rect(midbottom = (500,random_pipe_pos - 200))
    return bottom_pipe,top_pipe

def move_pipes(pipes):
    for pipe in pipes:
        pipe.centerx -= 5
    visible_pipes = [pipe for pipe in pipes if pipe.right > -50]
    return visible_pipes

def draw_pipes(pipes):
    for pipe in pipes:
        if pipe.bottom >= 550:
            screen.blit(pipe_surface,pipe)
        else:
            flip_pipe = pygame.transform.flip(pipe_surface,False,True)
            screen.blit(flip_pipe,pipe)
    return pipes

def check_collision(pipes):
    global can_score
    for pipe in pipes:
        if bird_rect.colliderect(pipe):
            can_score = True
            pygame.mixer.Sound.play(pygame.mixer.Sound('audio/hit.wav')).set_volume(0.15)
            pygame.mixer.Sound.play(pygame.mixer.Sound('audio/die.wav')).set_volume(0.6)
            return False
    if bird_rect.top <= -50 or bird_rect.bottom >= 570:
        can_score = True
        pygame.mixer.Sound.play(pygame.mixer.Sound('audio/hit.wav')).set_volume(0.15)
        pygame.mixer.Sound.play(pygame.mixer.Sound('audio/die.wav')).set_volume(0.6)
        return False
    
    return True

def rotate_bird(bird):
    new_bird = pygame.transform.rotozoom(bird,-bird_movement * 3,1)
    return new_bird

def bird_animation():
    new_bird = bird_frames[bird_index]
    new_bird_rect = new_bird.get_rect(center = (100,bird_rect.centery))
    return new_bird,new_bird_rect

def score_display(game_state):
    if game_state == "main_game":
      score_surface = game_font.render(str(data["score"]),True,(255,255,255))
      score_rect = score_surface.get_rect(center = (200,100))
      screen.blit(score_surface,score_rect)
    if game_state == "game_over":
      score_surface = game_font.render(f'Score: {data["score"]}',True,(255,255,255))
      score_rect = score_surface.get_rect(center = (200,100))
      #Author
      author_surface = game_font.render("GodOFPro",True,(255,255,255))
      author_rect = score_surface.get_rect(center = (200,20))
      screen.blit(score_surface,score_rect)
      screen.blit(author_surface,author_rect)

      high_score_surface = game_font.render(f'High score: {data["high_score"]}',True,(255,255,255))
      high_score_rect = high_score_surface.get_rect(center = (200,530))
      screen.blit(high_score_surface,high_score_rect)

def update_score(score, high_score,):
    if score > high_score:
        high_score = score
    if data["score"] > data["high_score"]:
        data["high_score"] = data["score"]
    return high_score

def draw_doublescore_powerup():
    global doublescore_sleep_duration
    doublescore_surface = pygame.image.load('sprites/2xcoinPixelart.png')
    doublescore_rect = doublescore_surface.get_rect(center = (30,500))
    doublescore_text = game_font.render(f': {str(doublescore_sleep_duration)} seconds',True,(255,255,255))
    doublescore_text_rect = doublescore_text.get_rect(center = (150,500))
    screen.blit(doublescore_surface,doublescore_rect)
    screen.blit(doublescore_text,doublescore_text_rect)

def pipe_score_check():
    global score, can_score, score_multi
    if pipe_list:
        for pipe in pipe_list:
            if 98 < pipe.centerx < 105 and can_score == True:
                score += 1
                score + score_multi
                data["score"] += 1 + score_multi
                can_score = False
                pygame.mixer.Sound.play(pygame.mixer.Sound('audio/point.wav')).set_volume(1.0)
                random_powerup()
            if pipe.centerx < 0:
                can_score = True

def display_fps():
    clock.tick()
    fps_surface =  game_font.render(f'FPS: {str(int(clock.get_fps()))}',True,(255,255,255))
    fps_rect = fps_surface.get_rect(center = (200,30))
    screen.blit(fps_surface,fps_rect)

def random_powerup():
    #Chances
    chance = random.randint(1,100)
    if chance <= 5:
     print("5 % chance of getting this")
     doublescore_timer_thread()
     
def doublescore_timer():
    global score_multi, doublescore_sleep_duration
    doublescore_sleep_duration = 3
    while doublescore_sleep_duration > 0:
        print(f"you have {doublescore_sleep_duration} seconds left")
        sleep(1)
        doublescore_sleep_duration -= 1
        score_multi = 1
    print("timer completed")
    score_multi = 0

def doublescore_timer_thread():
    doublescore_timer_thread = Thread(target=doublescore_timer)
    doublescore_timer_thread.start()

def quit():
    data["score"] = 0
    with open('score.txt','w') as score_file:
         json.dump(data,score_file)
    crypt_file()
    os.remove("score.txt")
    pygame.quit()
    sys.exit()

def main_menu():
    start_button = button.Button(50,100, start_img, 1.2)
    exit_button = button.Button(50,300, exit_img, 1.2)
    run = True
    while run:

        screen.fill((202, 228, 241))
        if start_button.draw(screen):
            run = False
        if exit_button.draw(screen):
            quit()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
        pygame.display.update()

clock = pygame.time.Clock()
pygame.init()
screen = pygame.display.set_mode((400,650))
game_font = pygame.font.Font('04B_19.ttf',30)
pygame.display.set_caption('Flappy Bird Made By GodOfPro')
#Icon 
game_icon = pygame.image.load('sprites/icon.png')
pygame.display.set_icon(pygame.image.load('sprites/icon.png'))

#Background Music
pygame.mixer.music.load("audio/music.mp3")
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.1)

# Game Variables
gravity = 0.15
bird_movement = 0
game_active = True
game_state = "main_menu"
score = 0
high_score = 0
can_score = True
score_multi = 0
doublescore_sleep_duration = 0
#Draw Variables

#Background
bg_surface = pygame.image.load('sprites/background-day.png').convert()
bg_surface = pygame.transform.smoothscale(bg_surface,(400,650))

#Floor
floor_surface = pygame.image.load('sprites/base.png').convert()
floor_surface = pygame.transform.smoothscale(floor_surface,(400,130))
floor_x_pos = 0
#Bird
bird_downflap = pygame.transform.scale(pygame.image.load('sprites/bluebird-downflap.png'),(42,30)).convert_alpha()
bird_midflap = pygame.transform.scale(pygame.image.load('sprites/bluebird-midflap.png'),(42,30)).convert_alpha()
bird_upflap = pygame.transform.scale(pygame.image.load('sprites/bluebird-upflap.png'),(42,30)).convert_alpha()
bird_frames = [bird_downflap,bird_midflap,bird_upflap]
bird_index = 0
bird_surface = bird_frames[bird_index]
bird_rect = bird_surface.get_rect(center = (100,325))

#Buttons
start_img = pygame.image.load("sprites/start_btn.png").convert_alpha()
exit_img = pygame.image.load("sprites/exit_btn.png").convert_alpha()

#Game Events
BIRDFLAP = pygame.USEREVENT + 1
pygame.time.set_timer(BIRDFLAP,200)
pipe_surface = pygame.image.load('sprites/pipe-green.png').convert()
pipe_surface = pygame.transform.smoothscale(pipe_surface,(62,320))
pipe_list = []
SPAWNPIPE = pygame.USEREVENT
pygame.time.set_timer(SPAWNPIPE,1200)
pipe_height = [300,250,350,400,450]
#Gameover Image
game_over_surface = pygame.image.load('sprites/message.png').convert_alpha()
game_over_rect = game_over_surface.get_rect(center = (200,325))
data = {
    'score': 0,
    'high_score': 0
}
# Read Json file to load the score 
try:
    decrypt_file()
    with open('score.txt') as score_file:
      data = json.load(score_file)
    os.remove("score.txt")
except:
    print("No File Has Been Created Yet")
#Game logic

if game_state == "main_menu":
    print("main_menu")
    main_menu()

if game_state == "game":
    print("game")

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_active == True:
                bird_movement = 0
                bird_movement -= 6
                pygame.mixer.Sound.play(pygame.mixer.Sound('audio/wing.wav')).set_volume(0.15)
            if event.key == pygame.K_SPACE and game_active == False:
                game_active = True
                pipe_list.clear()
                bird_rect.center = (100,325)
                bird_movement = 0
                score = 0
                data["score"] = 0
        if event.type == SPAWNPIPE:
            pipe_list.extend(create_pipe())
        if event.type == BIRDFLAP:
            if bird_index < 2:
                bird_index += 1
            else:
                bird_index = 0
            
            bird_surface,bird_rect = bird_animation()

    
    screen.blit(bg_surface,(0,0))
    if game_active:
        # Bird
        display_fps()
        bird_movement += gravity
        rotated_bird = rotate_bird(bird_surface)
        bird_rect.centery += bird_movement
        screen.blit(rotated_bird,bird_rect)
        game_active = check_collision(pipe_list)

        # Pipes
        pipe_list = move_pipes(pipe_list)
        draw_pipes(pipe_list)

        # Score
        pipe_score_check()
        high_score = update_score(score,high_score)
        score_display('main_game')
        draw_doublescore_powerup()

        
    else :
        screen.blit(game_over_surface,game_over_rect)
        score_display('game_over')
        

    # Floor
    floor_x_pos -= 0.7
    draw_floor()
    if floor_x_pos <= -400:
        floor_x_pos = 0
    
    pygame.display.update()
    clock.tick(120)


    
pygame.quit()