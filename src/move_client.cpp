#include <ros/ros.h>
#include <exp_assignment2/PlanningAction.h>
#include <actionlib/client/simple_action_client.h>
#include <actionlib/client/terminal_state.h>
#include <std_msgs/Float64.h>
#include <unistd.h>


int main(int argc, char** argv){
  ros::init(argc, argv, "simple_navigation_goals");
  ros::NodeHandle nh;

//dichiaro actionlib il nome del nodo e il tipo di messaggio
  actionlib::SimpleActionClient<exp_assignment2::PlanningAction> ac("/reaching_goal", true);

  
//publish an angle to the controller to rotate the camera
  //ros::Publisher pub = nh.advertise<std_msgs::Float64>("m2wr/joint1_position_controller/command", 10);

  //wait for the action server to come up
  while(!ac.waitForServer(ros::Duration(5.0))){
    ROS_INFO("Waiting for the move_base action server to come up");
  }
  
  double pos_x[22] = {7.0, 8.0, 7.0, 0.0,0.0, 5.0, 4.0, 0.0,4.0, 5.0, 0.0, 0.0,0.0, 4.0, 4.0, 0.0,0.0, 0.0,0.0, 4.0, 4.0, 0.0};
  double pos_y[22] = {0.0, 0.0, 0.0, 0.0,0.0, 7.0, 4.0, 0.0,0.0, 4.0, 4.0, 0.0,0.0, 7.0, 4.0, 0.0,4.0, 0.0,0.0, 7.0, 4.0, 0.0};
  double pos_z[22] = {0.25, 0.25, 0.25, 0.25,0.25, 0.25, 0.25, 0.25, -0.7, -0.7, 0.25, 0.25,0.25, -0.7, -0.7, -0.7,0.25, 0.25,0.25, -0.7, -0.7, -0.7};
  //double pos_x = {0.0000};
 // double pos_y = {1.000};
  //double pos_z = {0.25};

  exp_assignment2::PlanningGoal goal;
  
  
  for(int i=0;i<22;i++){
  std_msgs::Float64 angle;
  angle.data = 0.0;
  //we'll send a goal to move the robot
  goal.target_pose.header.frame_id = "link_chassis";
  goal.target_pose.header.stamp = ros::Time::now();

  goal.target_pose.pose.position.x = pos_x[i];
  goal.target_pose.pose.position.y = pos_y[i];
  goal.target_pose.pose.position.z = pos_z[i];
  goal.target_pose.pose.orientation.w = 0.0;

  ROS_INFO("Sending goal");
  ac.sendGoal(goal);

  ac.waitForResult();

  if(ac.getState() == actionlib::SimpleClientGoalState::SUCCEEDED)
    ROS_INFO("Hooray, target reached!");

  else
    ROS_INFO("The base failed to reach the target for some reason");
  
 // ROS_INFO("Rotating camera");
  //while(angle.data<6.27){
  //angle.data = angle.data +0.1;
  //pub.publish(angle);
  usleep(10);
  
  
  //ROS_INFO("Camera rotated");
    
  }
  return 0;
}
