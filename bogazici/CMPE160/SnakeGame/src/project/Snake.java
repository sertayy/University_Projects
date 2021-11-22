package project;

import java.awt.Color;
import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;
import javax.swing.JComponent;
import game.Direction;
import game.Drawable;
import naturesimulator.Action;
import naturesimulator.Action.Type;
import naturesimulator.LocalInformation;
import ui.GridPanel;

public class Snake implements Drawable{

	private Node head;
	LinkedList<Node> snakeParts = new LinkedList<Node>();
	public LinkedList<Node> getSnakeParts() {
		return snakeParts;
	}
	
	/**
	 * Constructs the coordinates of the snake's body
	 * @param head first node of the snake
	 * @param x1	   second node's x coordinate	
	 * @param x2	   third node's  x coordinate
	 * @param x3   last node's (tail) x coordinate
	 * @param y1	   second node's y coordinate
	 * @param y2   third node's y coordinate
	 * @param y3   last node's (tail) y coordinate
	 */
	public Snake(Node head, int x1, int x2, int x3, int y1, int y2, int y3) {
		
		this.head = head;
		snakeParts.add(head);
		addNode(x1,y1);
		addNode(x2,y2);
		addNode(x3,y3);	
	}
	
	/**
	 * adds the nodes to the snakeParts
	 * @param x
	 * @param y
	 */
	public void addNode(int x, int y) {
		snakeParts.add(new Node(x,y));
	}
	
	/**
	 * Returns the available action according to information
	 * @param information 
	 * @return action
	 */
	public Action chooseAction(LocalInformation information) {
		int headX = snakeParts.getFirst().getX();
		int headY = snakeParts.getFirst().getY();
		int foodX = information.getFood().getX();
		int foodY = information.getFood().getY();
		
		List<Direction> sensibleDirections = new ArrayList<Direction>();
 		List<Direction> freeDirections = information.getFreeDirections();
 		
		if (snakeParts.size()==8) {
			return new Action(Action.Type.REPRODUCE);
		}
			
		if(((headX - foodX) == 1) && (headY == foodY)) {
				return new Action(Type.EAT,Direction.LEFT);
		}else if (((headX - foodX) == -1) && (headY == foodY)) {
				return new Action(Type.EAT,Direction.RIGHT);
		}else if ((headX == foodX) && ((headY - foodY) == 1)) {
				return new Action(Type.EAT,Direction.UP);
		}else if ((headX == foodX) && ((headY - foodY) == -1)) {
				return new Action(Type.EAT,Direction.DOWN);
		}

		if(!freeDirections.isEmpty()){
			 if(headX > foodX && freeDirections.contains(Direction.LEFT))
				 sensibleDirections.add(Direction.LEFT);
			 if(headX < foodX && freeDirections.contains(Direction.RIGHT))
				 sensibleDirections.add(Direction.RIGHT);
			 if(headY > foodY && freeDirections.contains(Direction.UP))
				 sensibleDirections.add(Direction.UP);
			 if(headY < foodY && freeDirections.contains(Direction.DOWN))
				 sensibleDirections.add(Direction.DOWN);
			 if(!sensibleDirections.isEmpty()) {
				 return new Action(Action.Type.MOVE, LocalInformation.getRandomDirection(sensibleDirections));
			 }
			 return new Action(Action.Type.MOVE, LocalInformation.getRandomDirection(freeDirections));
		}
		return null;
	}
	
	/**
	 * Moves according to the direction
	 * @param direction
	 */
	public void move(Direction direction) {
		if(direction == Direction.UP) {
			snakeParts.addFirst(new Node(snakeParts.getFirst().getX(),snakeParts.getFirst().getY()-1));
			snakeParts.removeLast();
		} else if (direction == Direction.DOWN) {
			snakeParts.addFirst(new Node(snakeParts.getFirst().getX(),snakeParts.getFirst().getY()+1));
			snakeParts.removeLast();		
		} else if(direction == Direction.LEFT) {
			snakeParts.addFirst(new Node(snakeParts.getFirst().getX()-1,snakeParts.getFirst().getY()));
			snakeParts.removeLast();
		} else if(direction == Direction.RIGHT) {
			snakeParts.addFirst(new Node(snakeParts.getFirst().getX()+1,snakeParts.getFirst().getY()));
			snakeParts.removeLast();		
		}
	}		
	
	/**
	 * Snake eats the food
	 * @param food
	 */
	public void eat(Node food) {
		snakeParts.addFirst(new Node(food.getX(), food.getY()));		
	}	
	
	/**
	 * Creates a new snake including the last 4 nodes of a snake 
	 * Removes the last 4 nodes of the parent snake
	 * @return
	 */
	public Snake reproduce() {
		Node head = snakeParts.removeLast();
		Node body1 = snakeParts.removeLast();
		Node body2 = snakeParts.removeLast();
		Node body3 = snakeParts.removeLast();
		Snake newSnake = new Snake(head, body1.getX(), body2.getX(), body3.getX(), body1.getY(), body2.getY(), body3.getY());
		return newSnake;
	}	
	
	/**
	 * Draws snake
	 */
	@Override
	public void draw(GridPanel panel) {
		panel.drawSquare(snakeParts.get(0).getX(),snakeParts.get(0).getY(),Color.CYAN.brighter());
		for(int i=1; i< snakeParts.size(); i++) {
			panel.drawSquare(snakeParts.get(i).getX(),snakeParts.get(i).getY(),Color.GREEN.brighter());
		}
	}
}