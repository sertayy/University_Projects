package project;

import java.awt.Color;
import game.Direction;
import game.Drawable;
import naturesimulator.Action;
import naturesimulator.LocalInformation;
import ui.GridPanel;

public class Node implements Drawable{

	private int x;
    private int y;
/**
 * Node is the fundamental piece of the project
 * Constructs the coordinates
 * @param x
 * @param y
 */
    public Node(int x, int y) {
        this.x = x;
        this.y = y;
    }
    /**
     * Sets the x coordinate
     * @param x
     */
	public void setX(int x) {
		this.x = x;
	}
	/**
	 * Sets the y coordinate
	 * @param y
	 */
	public void setY(int y) {
		this.y = y;
	}
	/**
	 * Gets the x coordinate
	 * @return
	 */
	public int getX() {
        return x;
    }
	/**
	 * Gets the y coordinate
	 * @return
	 */
    public int getY() {
        return y;
    }
   /**
    * Draws node
    */
	@Override
	public void draw(GridPanel panel) {

	}
}