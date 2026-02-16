#importing packages
import random
import math
import turtle

STEPS_PER_SOLAR_RADIUS = 200
SCALE = 42000
PALETTE = [
    "cyan",
    "deepskyblue",
    "dodgerblue",
    "aqua",
    "turquoise",
    "springgreen",
    "lime",
    "chartreuse",
    "mediumspringgreen",
    "hotpink",
    "deeppink",
    "magenta",
    "violet",
    "orchid",
    "plum",
    "salmon",
    "coral",
    "tomato",
    "orange",
    "orangered",
    "white"
]


def createScreen():

    # If a previous turtle window died, force turtle to recreate its singleton screen
    try:
        turtle.TurtleScreen._RUNNING = True
        turtle.Turtle._screen = None
    except Exception:
        pass

    try:
        screen = turtle.Screen()
        screen.clearscreen()
    except turtle.Terminator:
        # try again after nuking cached screen
        turtle.Turtle._screen = None
        turtle.TurtleScreen._RUNNING = True
        screen = turtle.Screen()
        screen.clearscreen()

    screen.setup(width=1.0, height=1.0)
    screen.title("The Random Walk")
    screen.bgcolor("black")

    return screen

# create the star's turtle
def createStar(R_sol):
    steps_size = STEPS_PER_SOLAR_RADIUS * R_sol

    star = turtle.Turtle()
    star.speed(0)
    star.penup()
    star.color("yellow")
    star.goto(0, -steps_size)
    star.pendown()
    star.begin_fill()
    star.circle(steps_size)
    star.end_fill()
    star.hideturtle()
    return star


# create the background stars turtle
def createBackgroundStars(screen, n_stars):

    stars = []
    for _ in range(n_stars):
        t = turtle.Turtle(visible=False)
        t.speed(0)
        t.penup()
        t.color("yellow")
        t.goto(random.uniform(-720, 720), random.uniform(-404, 404))
        t.pendown()
        t.begin_fill()
        for _ in range(5):
            t.forward(10)
            t.right(144)
        t.end_fill()
        stars.append(t)
    screen.update()
    return stars

#creates a turtle for each photon
def createPhotons(screen, n_photons):
    
    photons = []
    for _ in range(n_photons):
        t = turtle.Turtle(visible=False)
        t.color(random.choice(PALETTE))
        t.speed(0)
        t.penup()
        t.goto(0, 0)
        t.pendown()
        photons.append(t)
    screen.update()
    return photons

#converts solar mass units into kilograms (SI units)
def getMass(M_sol):
    
    #convert solar units to SI units
    return 1.989e30*M_sol           #kg
    

#converts solar radius units into meters (SI units)
def getRadius(R_sol):
    
    #convert solar units to SI units
    return 6.95e8*R_sol           #meters
    

#calculates the density at the center of the star (SI units)
def getInitialDensity(M_SI, R_SI):
    
    #calculate the initial density of the star
    return (3*M_SI)/(math.pi*(R_SI**3))         # kg/m^3
    

#calculates the current density of star based on the photons current position (SI units)
def getCurrentDensity(rho_i, r, R):
    
    # linear profile, clamped to non-negative to avoid pathological steps
    return max(rho_i * (1 - (r / R)), 1e-12)

def getMeanFreePath(kappa, rho):
    return 1.0 / (kappa * rho)

def sampleStepLength(mean_free_path):
    u = random.random()
    return -mean_free_path * math.log(u)

def clamp(val, lo, hi):
    return max(lo, min(val, hi))

def clamp_with_msg(val, lo, hi, name):
    original = val
    val = clamp(val, lo, hi)
    if val != original:
        print(f"{name} adjusted to {val} (allowed range {lo}–{hi})")
    return val

def get_user_inputs():
    n_photons = clamp_with_msg(int(input("Photons: ")), 1, 25,"Photons")
    n_stars   = clamp_with_msg(int(input("Background stars: ")), 0, 100,"Background Stars")
    radius    = clamp_with_msg(float(input("Radius (R☉): ")), 0.2, 2.0,"Radius")
    mass      = clamp_with_msg(float(input("Mass (M☉): ")), 0.1, 25.0,"Mass")
    opacity   = clamp_with_msg(float(input("Opacity: ")), 0.1, 25.0,"Opacity")

    return n_photons, n_stars, mass, radius, opacity

def moveOnePhoton(photon, X, Y, r_steps, R_SI, kappa, rho_i, steps_to_SI):
    # convert current turtle radius (steps) -> SI radius (meters)
    r_SI = r_steps * steps_to_SI

    rho = getCurrentDensity(rho_i, r_SI, R_SI)
    mfp = getMeanFreePath(kappa, rho)
    step_SI = sampleStepLength(mfp)
    step = step_SI * SCALE

    theta = 2 * math.pi * random.random()
    X += step * math.cos(theta)
    Y += step * math.sin(theta)

    r_steps = math.sqrt(X * X + Y * Y)

    photon.goto(X, Y)
    return X, Y, r_steps


def movePhotons(screen, M_sol, R_sol, kappa, photons):
    M_SI = getMass(M_sol)
    R_SI = getRadius(R_sol)
    rho_i = getInitialDensity(M_SI, R_SI)
    
    steps_to_SI = R_SI / (R_sol * STEPS_PER_SOLAR_RADIUS)
    R_steps = STEPS_PER_SOLAR_RADIUS * R_sol

    X = [0.0] * len(photons)
    Y = [0.0] * len(photons)
    R = [0.0] * len(photons)

    furthest = 0.0
    while furthest <= R_steps:
        try:
            for i, p in enumerate(photons):
                X[i], Y[i], R[i] = moveOnePhoton(p, X[i], Y[i], R[i], R_SI, kappa, rho_i, steps_to_SI)
            screen.update()
        except turtle.Terminator:
            break

        furthest = max(R)

def closeSimulation(screen):
    # allow the user to exit graphic
    screen.exitonclick()

#function that takes in all user defined inputs, and simulates the photons' random walk
def simulateRandomWalk(n_photons, n_stars, M_sol, R_sol, kappa):
    screen = createScreen()
    screen.tracer(0,0)
    createStar(R_sol)
    createBackgroundStars(screen, n_stars)
    photons = createPhotons(screen, n_photons)

    movePhotons(screen, M_sol, R_sol, kappa, photons)
    closeSimulation(screen)


def main():
    args = get_user_inputs()
    simulateRandomWalk(*args)

if __name__ == "__main__":
    main()