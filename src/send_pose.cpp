#include <ros/ros.h>
#include <exp_assignment2/Num.h>
#include <exp_assignment2/PlanningAction.h>
#include <actionlib/client/simple_action_client.h>
#include <actionlib/client/terminal_state.h>
#include <std_msgs/Float64.h>
#include "std_msgs/String.h"
#include <sstream>
#include <std_msgs/Int8.h>

#include <unistd.h>

  ros::Publisher pub; //Publisher for sending velocity commands
  ros::Publisher pub2; //Publisher for sending velocity commands
void Callback (const exp_assignment2::Num::ConstPtr& msg) {
  ROS_INFO("received smth");

  actionlib::SimpleActionClient<exp_assignment2::PlanningAction> ac("/reaching_goal2", true);

//dichiaro actionlib il nome del nodo e il tipo di messaggio
  while(!ac.waitForServer(ros::Duration(5.0))){
    ROS_INFO("Waiting for the move_base action server to come up");
  }
  double x = 1.0 * msg->num[0];
  double y = 1.0 * msg->num[1];



  double pos_x = {x};
  double pos_y = {y};

  ROS_INFO("%f", pos_x);
  ROS_INFO("%f", pos_y);

  exp_assignment2::PlanningGoal goal;

  
  goal.target_pose.header.frame_id = "link_chassis";
  goal.target_pose.header.stamp = ros::Time::now();

  goal.target_pose.pose.position.x = pos_x;
  goal.target_pose.pose.position.y = pos_y;
  //goal.target_pose.pose.position.z = pos_z;
  goal.target_pose.pose.orientation.w = 0.0;

  ROS_INFO("Sending goal");
  ac.sendGoal(goal);

  ac.waitForResult();

  if(ac.getState() == actionlib::SimpleClientGoalState::SUCCEEDED)
  	ROS_INFO("Hooray, target reached!");


  
  else
  	ROS_INFO("The base failed to reach the target for some reason");

  std_msgs::Int8 msg2;
  msg2.data = 1;

  pub2.publish(msg2);

 // std_msgs::Float64 angle;
 // angle.data = 0.0;
  //ROS_INFO("Rotating camera");
  //while(angle.data<1){
//	angle.data=angle.data +0.1;
 //       pub.publish(angle);
  //      sleep(0.5);
  //}
  //sleep(5);
 // while(angle.data>=0){
//	angle.data=angle.data - 0.1;
  //      pub.publish(angle);
    //    sleep(0.5);
 // }

 
  
}
int main(int argc, char** argv){
  ros::init(argc, argv, "simple_navigation_goals");
  ros::NodeHandle nh;
  pub = nh.advertise<std_msgs::Float64>("/robot/joint1_position_controller/command", 10);
  pub2 = nh.advertise<std_msgs::Int8>("chatter", 1000);

  ros::Subscriber sub = nh.subscribe("targetPosition",4,Callback);//name of the topic, size of       buffer, callback
  ros::spin();
  
  return 0;
}
