# Assignment2_Exp

The aim of this project is to implement an architecture that simulates the behavior of a pet interacting with a ball moved by a human. The ball and the pet move in a 8x8 environment.
Depending on the interaction with the ball, the pet can be in 3 different states: normal, sleep, play. The normal state has as possible transitions both the sleep and the play state; instead, both sleep and play can only return to the normal state.

The architecture is composed by 5 nodes: send_pose, move_client, go_to_point_ball, go_to_point_action, state_machine. Its logic and the interaction between the nodes can be divided into 2. On one hand we have the nodes regarding the motion of the ball: move_client and go_to_point_ball. Inside these 2 nodes are implemented an action client and an action server respectively. The action client simply send some positions(i set the positions manually in order to possibly see the robot going through all the state in a short time), while the server move the robot in order to reach those positions.
The other 3 nodes handle the motion of the robot. The nodes send_pose and go_to_point_action are similar to the two described above. The action client send_pose receives positions from the state machine and send them to the action server go_to_point_action that moves the robot. 
The state_machine can be considered the main node, the one that handle all the transitions of the robot between the 3 states. 
In the normal behavior, random positions are sent to the node send_pose until the robot sees the ball(transition to the play state) or a certain time has passed( transition to the sleep state). 
In the sleep state a predefined position is sent to the send_pose node and the robot stays there for a certain time. After that it goes back to normal behavior.
In the play state, the robot keeps tracking the ball. When the ball stops, the robot turns the head, and after that it starts tracking the ball again. This behaviour is repeated until the robot is unable to find the ball for some time, and therefore it goes back to normal behaviour.
The 4 action nodes exchange messages of type Planning.action, while the other nodes exchange messages of type Num.msg. 

In the repository different folders are present: 
1)action and msg contain the types of messages just mentioned.
2)scripts and src contain the nodes explained above.
3)config contains a file for the configuration of the robot's motors.
4)urdf contains different files regarding the definition of the ball and the robot
5)launch contains a launch file to display everything.

To run the simulation only launching the launch file is needed.
When the simulation is launched, we can see from the terminal all the transitions between states displayed by the state_machine node.

The system has proved to be robust when stressed with randomness. To syncronize the state_machine node with the current behaviour of the robot, the state_machine stops everytime it sends a target position to the action client node, and will not go on with the execution until is notified that the just sent position has been reached by the robot. This avoid any kind of possible overlapping of commands that can lead to some weird behaviour of the robot. A consequence of this implementation can be observed when the robot is reaching a position(normal state) and in the meanwhile it sees the ball:it will not start tracking the ball(and enter in the play state) until it has reached the position.

I ran into a problem during the testing of the code. The action server(go_to_point_action) works properly(is pretty fast) when the connection with the action client remains active(hence, when the node state_machine sends positions sequentially). Instead, when the action client(send_pose) is not called for a certain time (for example during the play state) it always takes a couple of seconds before the action server can receive positions again and move the robot. 
This behaviour can be clearly noticed when the robot moves from the play to the normal state(looking at the terminal): when it enters the normal state a new target position is immediately sent to the action client, but the robot keeps rotating for some seconds before start reaching it. To make this behaviour even more clear, I displayed on the terminal an error message(just to make it more visible) everytime the action server actually receive the position sent by the client(in order to observe the delay).
Even if this behaviour doesn't cause any loss of data, it anyway delay the execution.
I couldn't find anything in the structure of the code that could explain this delay, but solving it could be an important improvement to the system.

Author: Cristina Naso Rappis
email:cri.tennis97@gmail.com
