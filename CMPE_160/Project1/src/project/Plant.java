package project;

import java.awt.Color;
import java.util.List;
import game.Direction;
import naturesimulator.Action;
import naturesimulator.LocalInformation;
import ui.GridPanel;

/**
 * The subclass of the creature that represents plants.
 */
public class Plant extends Creature {
	private static final double MAX_HEALTH = 1.0; // Maximum health limit that a plant can reach
	/**
	 * The constructor which gets the information from the creature class by calling super method
	 * @param x the coordinate of the plant in the x plane
	 * @param y the coordinate of the plant in the y plane
	 */
	public Plant(int x, int y) {
		super(x,y,MAX_HEALTH/2);
	}
	/**
	 * Gets the color of the particular square by using the interface
	 */
	public void draw(GridPanel panel) {
		panel.drawSquare(getX(),getY(), Color.RED);
	}
	/**
	 * Returns the available action that the plant can do
	 */ 
	@Override
	public Action chooseAction(LocalInformation information) {
		/**
		 * freeDirections list which gets the available directions from the information of the creature
		 * directionToMove chooses the direction from freeDirections randomly
		 */
		List<Direction> freeDirections = information.getFreeDirections();
		Direction directionToMove = LocalInformation.getRandomDirection(freeDirections);
		/**
		 * The plant chooses the reproduce action if its health is above the minimum health limit to reproduce and the directions around itself are empty
		 * Else it will choose stay action till it can reproduce
		 */
		if(this.getHealth() >= 0.75 && !freeDirections.isEmpty()) {
			Action action = new Action(Action.Type.REPRODUCE,directionToMove);
			return action;
		} else{
			Action action = new Action(Action.Type.STAY);
			return action;
		}
	}
		/**
		 * The action which allows the plant to reproduce and returns newborn plant
		 */
	@Override
	public Creature reproduce(Direction direction) {
		/**
		 * Gets the coordinates of the plant
		 */
		int x = getX();
		int y = getY();
		/**
		 * Then sets the available coordinates of the newborn plant according to the empty directions
		 */
		if(direction == Direction.UP) {
			y--;
		} else if (direction == Direction.DOWN) {
			y++;
		} else if(direction == Direction.LEFT) {
			x--;
		} else if(direction == Direction.RIGHT) {
			x++;
		}
		Plant child = new Plant(x,y); // Create a newborn plant
		child.setHealth(this.getHealth()/10.0); // Sets the health of each plant according to the rules
		this.setHealth(this.getHealth()*7.0/10.0);
		return child;
	}
		/**
		 * The action allows the plant to stay in the coordinates on that moment
		 * During stay action the plant's health is increasing 
		 */
	@Override
	public void stay() {
		setHealth(getHealth() + 0.05);
		if(getHealth() > MAX_HEALTH) {
			setHealth(MAX_HEALTH); // adjust the health if it exceeds the limit
		}
	}
}