#!/usr/bin/env python

import roslib
import rospy
from std_msgs.msg import String
from std_msgs.msg import Int8
from std_msgs.msg import Float64

import smach
import smach_ros
import time
import random
from exp_assignment2.msg import Num
import random
import datetime

import cv2
import sys
import time
import numpy as np
from scipy.ndimage import filters
import imutils
from sensor_msgs.msg import CompressedImage
from geometry_msgs.msg import Twist

VERBOSE = False



def user_action(data):
    
    if(data=='PLAY'):
	return ('play')

    elif(data=='SLEEP'):
	return ('sleep')

    elif(data=='NORMAL'):
	return ('normal')

   # else:
   #	return random.choice(['sleep','normal'])
  



# define state normal
class Normal(smach.State):
    def __init__(self):
        self.var='FALSE'
	self.count=0
	#self.gesture=[0,0]
	#get params from the parameter server
	#self.var= rospy.get_param('~person')
	#self.person = []
	#n = int(self.var[0])
	#self.person.append(n)
	#n = int(self.var[2])
	#self.person.append(n)
	#self.person = [2,2]
        time.sleep(6)
       # rospy.Subscriber('gesture', Num, self.callback)
        smach.State.__init__(self, 
                             outcomes=['play','sleep', 'normal'])


    def execute(self,userdata):
	
      	pub = rospy.Publisher('targetPosition', Num,queue_size=10)
        # subscribed Topic
        self.subscriber = rospy.Subscriber("camera1/image_raw/compressed",
                                           CompressedImage, self.callback,  queue_size=1)

        rospy.loginfo('Executing state NORMAL ')
	self.var='FALSE'
	#count=0

	while(self.var=='FALSE'):
        	#send the robot 3 random positions
		randomlist = []
		for i in range(0,2):
			n = random.randint(1,5)
			randomlist.append(n)
	        rospy.loginfo('sending the random position: %s', randomlist)		
		pub.publish(randomlist)
 		time.sleep(3)
		rospy.loginfo('still in NORMAL ')
                #to syncronize with the action client
		if(self.count>=1):
               		rospy.wait_for_message('chatter', Int8)

		self.count = self.count+1
		if self.count==4 :
			self.count=1
			self.var='FALSE'
			return user_action('SLEEP')	

	self.var='FALSE'
	self.subscriber.unregister()
	return user_action('PLAY')

		


    def callback(self,ros_data):
   
    #	rospy.loginfo('received image ')
	#next time we enter the normal state, the play state must be activated
    	#self.var = 'TRUE' 
	#self.gesture = data.num

 #### direct conversion to CV2 ####
        np_arr = np.fromstring(ros_data.data, np.uint8)
        image_np = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)  # OpenCV >= 3.0:

        greenLower = (50, 50, 20)
        greenUpper = (70, 255, 255)

        blurred = cv2.GaussianBlur(image_np, (11, 11), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, greenLower, greenUpper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        #cv2.imshow('mask', mask)
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        center = None
        # only proceed if at least one contour was found
        if len(cnts) > 0:
    		self.var = 'TRUE' 
	#else :
		#self.var = 'FALSE'
        

    


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


		

        #rospy.loginfo('sending the home position')
	pub.publish(self.home)	
        rospy.wait_for_message('chatter', Int8)	
	#add a sleep to make the robot remain in the sleep state for a certain time
	time.sleep(20)
        
        return user_action('NORMAL')
               
            


# define state play
class Play(smach.State):
    def __init__(self):
	
        smach.State.__init__(self, 
                             outcomes=['normal'])
        self.var2=0
	self.count=0
                          

    def execute(self,userdata):

	rospy.loginfo('Executing state PLAY')

        self.image_pub = rospy.Publisher("/output/image_raw/compressed",
                                         CompressedImage, queue_size=1)
        self.vel_pub = rospy.Publisher("cmd_vel",
                                       Twist, queue_size=1)
        self.publisher = rospy.Publisher("/robot/joint1_position_controller/command", Float64, queue_size=10)

        # subscribed Topic
        self.subscriber = rospy.Subscriber("camera1/image_raw/compressed",
                                           CompressedImage, self.callback2,  queue_size=1)

	self.lastTime = datetime.datetime.now().time()
	print(self.lastTime)
	while(self.var2<600):
		#rospy.loginfo('still in PLAY')
		self.count = self.count+1

	rospy.loginfo('stoptracking')
	self.var2=0
	self.subscriber.unregister()
	#time.sleep(5)
	return user_action('NORMAL')
           
    def callback2(self, ros_data):
   
    	#rospy.loginfo('received image ')

	#next time we enter the normal state, the play state must be activated
    	#self.var = 'TRUE' 
	#self.gesture = data.num

 #### direct conversion to CV2 ####
        np_arr = np.fromstring(ros_data.data, np.uint8)
        image_np = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)  # OpenCV >= 3.0:

        greenLower = (50, 50, 20)
        greenUpper = (70, 255, 255)

        blurred = cv2.GaussianBlur(image_np, (11, 11), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, greenLower, greenUpper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        #cv2.imshow('mask', mask)
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        center = None
        # only proceed if at least one contour was found
        if len(cnts) > 0:
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and
            # centroid
	    self.var2=0
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

            # only proceed if the radius meets a minimum size
            if radius > 10:
                # draw the circle and centroid on the frame,
                # then update the list of tracked points
                cv2.circle(image_np, (int(x), int(y)), int(radius),
                           (0, 255, 255), 2)
                cv2.circle(image_np, center, 5, (0, 0, 255), -1)
                vel = Twist()
                vel.angular.z = -0.002*(center[0]-400)
                vel.linear.x = -0.01*(radius-100)
                self.vel_pub.publish(vel)
	       # print(vel)
	        currentTime = datetime.datetime.now().time()
		print(currentTime)
                delta = datetime.timedelta(seconds = 7)
	
		if (vel.angular.z<0.05 and vel.angular.z>-0.05 and vel.linear.x<0.05 and vel.linear.x>-0.05 and currentTime>(datetime.datetime.combine(datetime.date(1,1,1),self.lastTime)+ 			delta).time()):

			  angle = Float64()
  			  angle.data = 0.0
  			  rospy.loginfo("Rotating camera")
  			  while(angle.data<1):
				angle.data=angle.data +0.1
       		                self.publisher.publish(angle)
                                time.sleep(0.5);
  
                          time.sleep(5);
                          while(angle.data>=0):
	                  	angle.data=angle.data - 0.1
                      	        self.publisher.publish(angle)
        			time.sleep(0.5)
			  self.lastTime = datetime.datetime.now().time()		

            else:
                vel = Twist()
                vel.linear.x = 0.5
                self.vel_pub.publish(vel)

        else:
	    self.var2 = self.var2+1
            vel = Twist()
            vel.angular.z = 0.5
            self.vel_pub.publish(vel)

        #cv2.imshow('window', image_np)
        #cv2.waitKey(2)

        # self.subscriber.unregister()



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
