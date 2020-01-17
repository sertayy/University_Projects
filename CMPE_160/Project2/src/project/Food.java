package project;

import java.awt.Color;
import java.util.List;
import game.Direction;
import game.Drawable;
import naturesimulator.Action;
import naturesimulator.LocalInformation;
import ui.GridPanel;

public class Food extends Node implements Drawable  {
	
	private int x;
	private int y;

	/**
	 * Food is a Node
	 * Constructs the coordinates
	 */
	public Food(int x, int y) {
	super(x,y);
	}
	
	/**
	 * Draws food
	 */
	public void draw(GridPanel panel) {
		panel.drawSquare(getX(),getY(), Color.YELLOW.brighter());
	}
}