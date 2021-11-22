package project;

import java.awt.Color;
import java.util.ArrayList;
import java.util.List;
import game.Direction;
import naturesimulator.Action;
import naturesimulator.LocalInformation;
import ui.GridPanel;

/** 
 * The subclass of the creature that represents herbivores.
 */
public class Herbivore extends Creature {
	private static final double MAX_HEALTH = 20.0; // Maximum health limit that a herbivore can reach
	/**
	 * The constructor which gets the information from the creature class by calling super method
	 * @param x the coordinate of the herbivore in the x plane
	 * @param y the coordinate of the herbivore in the y plane
	 */
	public Herbivore(int x, int y) {
		super(x,y,MAX_HEALTH/2);
	}
	/**
	 * Gets the color of the particular square by using the interface.
	 * if the herbivore's health is under the particular level its color is red else blue.
	 */
	public void draw(GridPanel panel) {
		if(getHealth()>15) {
			panel.drawSquare(getX(),getY(),Color.blue);
		}
		else{
			panel.drawSquare(getX(),getY(),Color.GRAY);
		}
	}
	/**
	 * Returns the available action that the herbivore can do.
	 */
	@Override
	public Action chooseAction(LocalInformation information) {
		/**
		 * freeDirections list which gets the available directions from the information of the creature.
		 * directionToMove chooses the direction from freeDirections randomly.
		 */
		List<Direction> freeDirections = information.getFreeDirections();
		Direction directionToMove = LocalInformation.getRandomDirection(freeDirections);
		/**
		 * The herbivore chooses the reproduce action if its health is equals the maximum health limit and the directions around itself are empty.
		 */
		if(this.getHealth() == MAX_HEALTH && !freeDirections.isEmpty()){
			Action action = new Action(Action.Type.REPRODUCE,directionToMove);
			return action;
		}/**
		* if it can not reproduce, it chooses attack action.
		* Herbivore attacks one of the plants around itself and chooses the plant randomly.  
		*/
		else if(isPlant(information)){
			/** Attack array list are composed of the plants' directions which the herbivore can attack.
			 */
			ArrayList<Direction> attack = new ArrayList<Direction>();
			/**
			 * if the creature around herbivore is plant, the direction of the plant is added to the attack list.
			 */
			  if(information.getCreatureDown() instanceof Plant) { 
				attack.add(Direction.DOWN);
			} if(information.getCreatureUp() instanceof Plant) {
				attack.add(Direction.UP);
			} if(information.getCreatureLeft() instanceof Plant) {
				attack.add(Direction.LEFT);
			} if(information.getCreatureRight() instanceof Plant) {
				attack.add(Direction.RIGHT);
			}
			Action action = new Action(Action.Type.ATTACK,LocalInformation.getRandomDirection(attack)); // herbivore chooses the plant randomly
			return action;
		}/**
		* if it can not attack and there is an empty direction and its health is above the particular level, it chooses the move action.
		* Herbivore chooses one of the directions randomly.
		*/
		else if(!freeDirections.isEmpty() && getHealth() > 1.0){
			Action action = new Action(Action.Type.MOVE,directionToMove);
			return action;
		}/**
		* if the herbivore can not do one of the actions above, it chooses to stay.
		* During stay action the herbivore's health is decreasing. 
		*/
		else{
			Action action = new Action(Action.Type.STAY);
			return action;
		}
	}
		/**
		 * The action which allows the herbivore to reproduce and returns a newborn plant.
		 */
	@Override
	public Creature reproduce(Direction direction) {
		/**
		 * Gets the coordinates of the herbivore.
		 */
		int x = getX();
		int y = getY();
		/**
		 * Then sets the available coordinates of the newborn herbivore according to the empty directions.
		 */
		if(direction == Direction.UP) {
			y--;
		} else if (direction ==Direction.DOWN) {
			y++;
		} else if(direction == Direction.LEFT) {
			x--;
		} else if(direction == Direction.RIGHT) {
			x++;
		}
		this.setHealth(8.0); // Sets the parent herbivore's health according to the rules.
		Herbivore child = new Herbivore(x,y); // Create a newborn herbivore.
		child.setHealth(4.0); // Sets the newborn herbivore's health according to the rules.
		return child;
	}
		/**
		 * The action that allows the herbivore to move in the available direction.
		 * During the action herbivore's health is decreasing.
		 */
	@Override
	public void move(Direction direction) {
			setHealth(getHealth()-1.0);
			/**
			 * Sets the new coordinates according to empty directions.
			 * Herbivore chooses the new direction randomly.
			 */
			if(direction == Direction.UP) {
			setY(getY()-1);
		} 
			else if (direction == Direction.DOWN) {
			setY(getY()+1);
		}
			else if(direction == Direction.LEFT) {
			setX(getX()-1);
		}
			else if(direction == Direction.RIGHT) {
			setX(getX()+1);
		}
	}	
		/**
		 * The action that allows the herbivore to attack.
		 * The health of the plant is added to the herbivore's health.
		 * The herbivore moves to the coordinates of the attacked plant and the plant's health gets zero.
		 */
	@Override
	public void attack(Creature creature) {
		setHealth(creature.getHealth() + getHealth());
		if(getHealth()>MAX_HEALTH) {
			setHealth(MAX_HEALTH); // Adjust the health if it exceeds the limit.
		}
		setX(creature.getX()); // Sets the new coordinates of herbivore according to the plant's coordinates.
		setY(creature.getY());
		creature.setHealth(0);  // The plant is dead.
	}
		/**
		 * The method to determine the creature around herbivore.
		 * if it is plant it returns true otherwise it returns false.
		 * @param information the information about the herbivore on that moment.
		 * @return 
		 */
	public boolean isPlant(LocalInformation information) {
		if(information.getCreatureDown()!=null && information.getCreatureDown() instanceof Plant) {
			return true;
		} else if(information.getCreatureUp()!=null && information.getCreatureUp() instanceof Plant) {
			return true;
		} else if(information.getCreatureRight()!=null && information.getCreatureRight() instanceof Plant) {
			return true;
		} else if(information.getCreatureLeft()!=null && information.getCreatureLeft() instanceof Plant) {
			return true;
		}
		return false;
	}
	/**
	 * The action allows the herbivore to stay in the coordinates on that moment.
	 * During stay action the herbivore's health is decreasing.
	 */
	@Override
	public void stay() {
		setHealth(getHealth() - 0.1);
	}
}