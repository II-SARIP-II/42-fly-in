_This project has been created as part of the 42 curriculum by pgougne_

# Description
## 1) Introduction
Drones have been used to herd sheep in New Zealand, replacing sheepdogs with buzzing aerial shepherds. In Japan, office buildings deploy drones that play loud music and flashlights to literally chase overworked employees home. One drone was trained to paint graffiti on walls mid-flight — a rebellious blend of tech and street art. In Sweden, scientists used drones to sniff out whale poop floating on the ocean to study endangered species. Some experimental drones are shaped like birds or insects to spy without being noticed, flapping wings and all. There’s even a drone that flies by flapping soap bubbles, no propellers involved. In volcano research, a drone once flew straight into an eruption cloud, melted mid-air, but managed to send back data just seconds before disintegration. And in South Korea, synchronized drone shows have replaced fireworks — safer, silent, and somehow even more magical.

The phrase comes from the idea that the wheel is a brilliant invention that’s been around forever and works really well. Since there’s nothing wrong with it, trying to invent it again wouldn’t really help and could be a waste of time—especially when that time could be spent solving new problems instead.

In programming, this happens when someone builds something from scratch that already exists — like writing your own sorting algorithm or framework when solid, open-source versions are already out there. But it’s not all bad: doing it yourself can be a great way to learn how things work under the hood. The key is to find a balance — don’t rebuild everything, but take time to explore how the tools you’re using actually work. That way, you’ll grow as a developer without getting stuck reinventing the same old wheels.

## 2) Project
Autonomous drones are the future of transportation. They are already used in many industries, such as agriculture, construction, and logistics. They are also used in military
operations, such as surveillance and reconnaissance.

My task was to design a system that efficiently routes a fleet of drones from a central base (start) to a target location (end), while navigating this dynamic network under a set of strict constraints and optimization goals.

I've been given a graph representing the network of zones, and a set of constraints that you must respect.

The graph is represented as a network of connected zones, where connections define possible movement paths between zones

For this project, I used:

- Pydantic -> parsing
- Pygame -> Visualisation

graph solving:

1) reverse dijkstra
2) Greedy Best-First Search

Personnal choice:
To solve the graph i decided that the priority rule is choosen if the path is free and the lenght of the path is smaller or the same than other possible path that are not flagged as priority.

# Instructions
run the program
>Make run


# Resources

# Algorythm Description

# Visualisation features
