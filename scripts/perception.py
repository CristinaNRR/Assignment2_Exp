#!/usr/bin/env python
# Software License Agreement (BSD License)
#
# Copyright (c) 2008, Willow Garage, Inc.
# All rights reserved.
#


import rospy
from std_msgs.msg import String
from exp_assignment2.msg import Num
import random
import time

#send e gesture every tot ms
def perception():
    pub = rospy.Publisher('gesture', Num)
    rospy.init_node('perception', anonymous=True)
   
  
    while not rospy.is_shutdown():

		randomGesture = []
		for i in range(0,2):
			n = random.randint(1,10)
			randomGesture.append(n)
		pub.publish(randomGesture)
     		print(randomGesture)   
		
		rand = random.randint(1,15)	
		time.sleep(rand)
                


if __name__ == '__main__':
    try:
        perception()
    except rospy.ROSInterruptException:
        pass
