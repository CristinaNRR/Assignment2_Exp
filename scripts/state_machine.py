#!/usr/bin/env python

import roslib
import rospy
from std_msgs.msg import String

import smach
import smach_ros
import time
import random
from exp_assignment2.msg import Num
import random



def user_action(data):
    
    if(data=='PLAY'):
	return ('play')

    elif(data=='NORMAL'):
	return ('normal')

    else:
   	return random.choice(['sleep','normal'])
  



# define state normal
class Normal(smach.State):
    def __init__(self):
        self.var='FALSE'
	self.gesture=[0,0]
	#get params from the parameter server
	#self.var= rospy.get_param('~person')
	#self.person = []
	#n = int(self.var[0])
	#self.person.append(n)
	#n = int(self.var[2])
	#self.person.append(n)
	self.person = [2,2]
        
        rospy.Subscriber('gesture', Num, self.callback)
        smach.State.__init__(self, 
                             outcomes=['play','sleep', 'normal'])


    def execute(self,userdata):
      	pub = rospy.Publisher('targetPosition', Num,queue_size=10)

        rospy.loginfo('Executing state NORMAL ')
  	time.sleep(3)

	count=0
	while(count<3):
        	#send the robot 3 random positions
		randomlist = []
		for i in range(0,2):
			n = random.randint(1,5)
			randomlist.append(n)
		rospy.loginfo('sending the random position: %s', randomlist)		
		pub.publish(randomlist)
		count= count+1
	#if we received a gesture position
	if(self.var=='TRUE'):
		#send the robot the gesture and person position and activate the play state            
		#pub.publish(self.person)
		rospy.loginfo('sending the person position: %s', self.person)		
                #pub.publish(self.gesture)
		rospy.loginfo('sending the gesture position:%s', self.gesture)
                pub.publish(self.person)
		rospy.loginfo('sending the person position:%s', self.person)

		self.var='FALSE'
		return user_action('PLAY')
	else:
		
		#activate sleep or normal
        	return user_action('Random')

    def callback(self,data):
   
    	rospy.loginfo('gesture position: %s', data.num)

   
	#next time we enter the normal state, the play state must be activated
    	self.var = 'TRUE' 
	self.gesture = data.num
        

    


#the robot goes to a predifined position and stays there for a certain time. After that it goes to the normal behavour
class Sleep(smach.State):
    def __init__(self):
        smach.State.__init__(self, 
                             outcomes=['normal'])

	#get params from the parameter server
	#self.var= rospy.get_param('~home')
	#self.home = []
	#n = int(self.var[0])
	#self.home.append(n)
	#n = int(self.var[2])
	#self.home.append(n)
        self.home = [3,3]

    def execute(self,userdata):
        rospy.loginfo('Executing state SLEEP')
        pub = rospy.Publisher('targetPosition', Num,queue_size=10) 
        while not rospy.is_shutdown():  
		

		rospy.loginfo('sending the home position: %s', self.home)
		pub.publish(self.home)		
		#add a sleep to make the robot remain in the sleep state for a certain time
		time.sleep(5)
        
                return user_action('NORMAL')
               
            


# define state play
class Play(smach.State):
    def __init__(self):
	
        smach.State.__init__(self, 
                             outcomes=['normal'])
                          

    def execute(self,userdata):

	rospy.loginfo('Executing state PLAY')
        time.sleep(5)
        return user_action('NORMAL')
           


class func():
  def __init__(self):
        
                       
    rospy.init_node('state_machine') 

  
    # Create a SMACH state machine
    sm = smach.StateMachine(outcomes=['container_interface'])
   

    # Open the container
    with sm:
        # Add states to the container
        smach.StateMachine.add('NORMAL', Normal(), 
                               transitions={'normal':'NORMAL', 
                                            'play':'PLAY',
				             'sleep' : 'SLEEP'})
                                              
        smach.StateMachine.add('PLAY', Play(), 
                               transitions={'normal':'NORMAL' 
                                             })
	smach.StateMachine.add('SLEEP', Sleep(), 
                               transitions={'normal':'NORMAL'})
                               
                               

    # Create and start the introspection server for visualization
    sis = smach_ros.IntrospectionServer('server_name', sm, '/SM_ROOT')
    sis.start()

    # Execute the state machine
    outcome = sm.execute()

    # Wait for ctrl-c to stop the application
    rospy.spin()
    sis.stop()

 

if __name__ == '__main__':
    
    func()
