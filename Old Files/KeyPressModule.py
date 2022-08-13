import pygame

def init():
    pygame.init()
    win = pygame.display.set_mode((100, 100))

def getKey(keyName):
    ans = False
    for eve in pygame.event.get() : pass
    keyInput = pygame.key.get_pressed()


    #print(keyInput)
    #print(pygame)

    myKey = getattr(pygame, 'K_{}'.format(keyName))

    #pygame.K_

    #<<위의 코드는 myKey = pygame.K_LEFT 와 같다. pygame이라는 오브젝트 안에서 뽑아온 것.>>
    #print(pygame.K_LEFT)
    #print(keyInput[myKey])

    if keyInput[myKey]:
        ans = True
    pygame.display.update()

    return ans

def main():
    if getKey("LEFT"):
        print("Left key pressed")
    if getKey("RIGHT"):
        print("Right key pressed")
    if getKey("KP_ENTER"):
        print("ENTER key pressed")


if __name__ == '__main__':
    init()
    while True: main()