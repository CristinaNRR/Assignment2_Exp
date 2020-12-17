#include <ros/ros.h>
#include <exp_assignment2/PlanningAction.h>
#include <actionlib/client/simple_action_client.h>
#include <actionlib/client/terminal_state.h>
#include <std_msgs/Float64.h>
#include <unistd.h>


int main(int argc, char** argv){
  ros::init(argc, argv, "simple_navigation_goals");
  ros::NodeHandle nh;

//declare an actionlib client
  actionlib::SimpleActionClient<exp_assignment2::PlanningAction> ac("reaching_goal", true);

  //wait for the action server to come up
  while(!ac.waitForServer(ros::Duration(5.0))){
    ROS_INFO("Waiting for the move_base action server to come up");
  }
  
//define some goal position for the ball
  double pos_x[29] = {7.0, 8.0, -7.0, 0.0,3.0, 0.0, 4.0, 0.0,4.0, -5.0, 0.0, 0.0,0.0, 4.0, 4.0, 0.0,0.0, 0.0,0.0, -4.0, 4.0, 0.0, 7.0, 8.0, -7.0, 0.0,4.0, 0.0, 4.0};
  double pos_y[29] = {0.0, -1.0, 0.0, -5.0,0.0, 0.0, -4.0, 0.0,0.0, 4.0, 4.0, 0.0,0.0, -7.0, 4.0, 0.0,4.0, 0.0,0.0, 7.0, 4.0, 0.0,0.0, -1.0, 0.0, -5.0,0.0, 0.0, -4.0};
  double pos_z[29] = {0.25, 0.25, 0.25, 0.25,0.25, 0.25, 0.25, 0.25, -0.7, -0.7, 0.25, 0.25,0.25, -0.7, -0.7, 0.25,0.25, 0.25,0.25, -0.7, -0.7, 0.25,0.25, 0.25, 0.25, 0.25,0.25, 0.25, 0.25};
 

  exp_assignment2::PlanningGoal goal;
  
  
  for(int i=0;i<29;i++){
  std_msgs::Float64 angle;
  angle.data = 0.0;
  goal.target_pose.header.frame_id = "base_link";
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
  

  sleep(5);
  
  }  
  
  return 0;
}
