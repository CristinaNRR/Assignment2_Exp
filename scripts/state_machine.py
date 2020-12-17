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




def user_action(data):
    
    if(data=='PLAY'):
	return ('play')

    elif(data=='SLEEP'):
	return ('sleep')

    elif(data=='NORMAL'):
	return ('normal')

   




#In the normal state the robot reaches random positions. After a certain time move to the sleep behaviour.
#when it sees the ball it moves to the play behavior

class Normal(smach.State):


    def __init__(self):
        self.var='FALSE'
	self.count=0
        #wait some seconds when we launch the program
        time.sleep(6)
        smach.State.__init__(self, 
                             outcomes=['play','sleep'])


    def execute(self,userdata):

        rospy.loginfo('Executing state NORMAL ')
	#send to the actionlib client the target positions to reach
      	pub = rospy.Publisher('targetPosition', Num,queue_size=10)
        # subscribed to the camera topic
        self.subscriber = rospy.Subscriber("camera1/image_raw/compressed",
                                           CompressedImage, self.callback,  queue_size=1)


	self.var='FALSE'
	while(self.var=='FALSE'):
        	#send the robot random positions
		randomlist = []
		for i in range(0,2):
			n = random.randint(-7,7)
			randomlist.append(n)
	        rospy.loginfo('sending the random position: %s', randomlist)		
		pub.publish(randomlist)
 		time.sleep(3)
                #to syncronize with the action client
		if(self.count>=1):
			#stop until the just sent target has been reached
               		rospy.wait_for_message('chatter', Int8)

		self.count = self.count+1
		#after some actions have been executed go to the sleep state
		if self.count==4 :
			self.count=1
			self.var='FALSE'
			return user_action('SLEEP')	

	#when the robot sees the ball, move to the play state
	self.var='FALSE'
	#unsubscribe to the camera topic to avoid overlapping
	self.subscriber.unregister()
	return user_action('PLAY')

		


    def callback(self,ros_data):
   

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
	#put a flag to true when the robot sees the ball
        if len(cnts) > 0:
    		self.var = 'TRUE' 
	
        
   



#In the sleep state the robot goes to a predifined position and stays there for a certain time. After that it goes to the normal behavior

class Sleep(smach.State):

    def __init__(self):
        smach.State.__init__(self, 
                             outcomes=['normal'])


        self.home = [3,3]

    def execute(self,userdata):
        rospy.loginfo('Executing state SLEEP')
	#send the actionlib client the target position to reach
        pub = rospy.Publisher('targetPosition', Num,queue_size=10) 
	pub.publish(self.home)	
        rospy.wait_for_message('chatter', Int8)	
	#add a sleep to make the robot remain in the sleep state for a certain time
	time.sleep(20)
        
        return user_action('NORMAL')
               
            


#In the play state the robot keeps tracking the ball. When the ball stops it moves the head.
#It goes back to the normale behaviour when it canno't find the ball for a certain amount of time

class Play(smach.State):

    def __init__(self):
	
        smach.State.__init__(self, 
                             outcomes=['normal'])
        self.var2=0
	self.count=0
                          

    def execute(self,userdata):

	rospy.loginfo('Executing state PLAY')

       # self.image_pub = rospy.Publisher("/output/image_raw/compressed",
        #                                 CompressedImage, queue_size=1)
        self.vel_pub = rospy.Publisher("cmd_vel",
                                       Twist, queue_size=1)
        self.publisher = rospy.Publisher("/robot/joint1_position_controller/command", Float64, queue_size=10)

       
        self.subscriber = rospy.Subscriber("camera1/image_raw/compressed",
                                           CompressedImage, self.callback2,  queue_size=1)

	self.lastTime = datetime.datetime.now().time()

	while(self.var2<600):
		self.count = self.count+1

	#go back to normal behaviour
	rospy.loginfo('stop tracking the ball')
	self.var2=0
	self.subscriber.unregister()
	return user_action('NORMAL')
           
    def callback2(self, ros_data):
  

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
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        center = None
        # only proceed if at least one contour was found
        if len(cnts) > 0:
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and
            # centroid

	    #put the variable to 0 when the robot sees the ball
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
	        currentTime = datetime.datetime.now().time()
                delta = datetime.timedelta(seconds = 7)

		#rotate the camera if the robot is not moving	  
		if (vel.angular.z<0.03 and vel.angular.z>-0.03 and vel.linear.x<0.03 and vel.linear.x>-0.03 and currentTime>(datetime.datetime.combine(datetime.date(1,1,1),self.lastTime)+ 			delta).time()):

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
	    #increment a variable everytime the robot doesn't see the ball
	    self.var2 = self.var2+1
            vel = Twist()
            vel.angular.z = 0.5
            self.vel_pub.publish(vel)




class func():
  def __init__(self):
        
                       
    rospy.init_node('state_machine') 

  
    # Create a SMACH state machine
    sm = smach.StateMachine(outcomes=['container_interface'])
   

    # Open the container
    with sm:
        # Add states to the container
        smach.StateMachine.add('NORMAL', Normal(), 
                               transitions={
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
