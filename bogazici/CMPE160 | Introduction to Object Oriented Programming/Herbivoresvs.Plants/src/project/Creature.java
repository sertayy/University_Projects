package project;

import java.util.List;
import game.Direction;
import game.Drawable;
import naturesimulator.Action;
import naturesimulator.LocalInformation;
import ui.GridPanel;

/**
 * The super class of plant and herbivore classes.
 */
public abstract class Creature implements Drawable {
	
	private int x;
	private int y;
	private double health;
	/**
	 * Constructs the fields for determining the coordinates and the health of the creature for further processes.
	 * @param x the coordinate in the x plane
	 * @param y the coordinate in the y plane
	 * @param health the health of the creature
	 */
	public Creature(int x, int y, double health) {
		this.x = x;
		this.y = y;
		this.health = health;
	}
	
	public Creature (int x, int y) {
		this.x = x;
		this.y = y;
	}
	/**
	 * Setter for the x coordinate of the creature
	 * @param x
	 */
	public void setX(int x) {
		this.x = x;
	}
	/**
	 * Setter for the y coordinate of the creature
	 * @param y
	 */
	public void setY(int y) {
		this.y = y;
	}
	/**
	 * Setter for the health of the creature
	 * @param health
	 */
	public void setHealth(double health) {
		this.health = health;
	}
	/**
	 * Allows the creatures to be drawn on the grid panel thanks to drawable interface.
	 */
	public void draw(GridPanel panel) {
	}
	/**
	 * Getter for the x coordinate of the creature
	 * @return the x coordinate
	 */
	public int getX() {
		return x;
	}
	/**
	 * Getter for the y coordinate of the creature
	 * @return the y coordinate
	 */
	public int getY() {
		return y;
	}
	/**
	 * Getter for the health of the creature
	 * @return the health 
	 */
	public double getHealth() {
		return health;
	}
	/**
	 * Chooses the action which the creature can do
	 * @param information informing about creatures
	 * @return will return action in the plant and herbivore classes
	 */
	public Action chooseAction(LocalInformation information) {
		return null;
	}
	/**
	 * the action which allows the creature to stay in the coordinates on that moment 
	 */
	public void stay() {
	}
	/**
	 * the action which allows the creature to reproduce
	 * @param direction will be used for determining the newborn creature's coordinates
	 * @return the newborn creature 
	 */
	public Creature reproduce(Direction direction) {
		
		return null;
	}
	/**
	 * the action which allows the herbivore to move
	 * @param direction directs the herbivore to new coordinates
	 */
	public void move(Direction direction) {
	}
	/**
	 * the action which allows the herbivore to attack the plants
	 * @param attackedCreature the plant which get attacked
	 */
	public void attack(Creature attackedCreature) {
	}
}