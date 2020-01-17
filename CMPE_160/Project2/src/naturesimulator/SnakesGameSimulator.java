package naturesimulator;

import game.Direction;
import game.GridGame;
import project.Food;
import project.Node;
import project.Snake;
import ui.GridPanel;
import java.awt.Color;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;

/**
 * Class that implements the game logic for Snakes.
 */
public class SnakesGameSimulator extends GridGame {
	
	/**
	 * Creates a new Snakes game instance
	 * @param gridWidth number of grid squares along the width
	 * @param gridHeight number of grid squares along the height
	 * @param gridSquareSize size of a grid square in pixels
	 * @param frameRate frame rate (number of timer ticks per second) 
	 */
	private Food food;
	private List<Snake> snakes;
	private	Node[][] nodesMap;
	
	public SnakesGameSimulator(int gridWidth, int gridHeight, int gridSquareSize, int frameRate) {
		super(gridWidth, gridHeight, gridSquareSize, frameRate);
		int x = (int) (Math.random() * getGridWidth());
		int y = (int) (Math.random() * getGridHeight());
		
		//initialized
		food = new Food(x,y);
		snakes = new ArrayList<>();
		nodesMap = new Node[gridWidth][gridHeight];
	} 
	
	/**
	 * this method is called by the gridGame in each iteration
	 */
	@Override
	protected void timerTick() {
		
		// Determine and execute actions for all snakes
		ArrayList<Snake> snakesCopy = new ArrayList<>(snakes);
		for (Snake snake: snakesCopy) {
			// Choose action
			Action action = snake.chooseAction(createLocalInformationForNode(snake.getSnakeParts().get(0)));
			if(action != null) {
				// Execute action				
				if (action.getType() == Action.Type.MOVE) {
					// Controls the direction of snake's first node (head) 
					// gets the direction and moves
					if (isDirectionFree(snake.getSnakeParts().get(0).getX(), snake.getSnakeParts().get(0).getY(), action.getDirection())) {
						nodesMap[snake.getSnakeParts().getLast().getX()][snake.getSnakeParts().getLast().getY()] = null;
						snake.move(action.getDirection());
						updateNodesMap(snake);
						addDrawable(snake);
					}
				} else if(action.getType() == Action.Type.EAT) {
					// Node eaten corresponds to eaten food
					Node eaten = getNodeAtPosition(food.getX(), food.getY());
					// if the food is not eaten, it calls eat action
					if (eaten != null) {
						
						removeDrawable(food);
						removeNode(getNodeAtPosition(food.getX(), food.getY()));	
						snake.eat(eaten);
						updateNodesMap(snake);
						addDrawable(snake); 
						int x = (int) (Math.random() * getGridWidth());
						int y = (int) (Math.random() * getGridHeight());
						// adds the food into the null node
						while(!(nodesMap[x][y] == null)) {
							 x = (int) (Math.random() * getGridWidth());
							 y = (int) (Math.random() * getGridHeight());
						}
						addFood(x, y); 
					}  
				} 
//				else if(action.getType() == Action.Type.REPRODUCE) {
//					// Creates a newSnake
//					Snake newSnake = snake.reproduce();
//					snakes.add(newSnake);
//					updateNodesMap(snake);
//					addDrawable(newSnake);
//					updateNodesMap(newSnake);
//				}
			}
		}
		
	}
	
	/**
	 * 	Adds first snake to the game
	 */
	public void addSnake () {
		Snake snake = new Snake(new Node(4,1), 3, 2, 1, 1, 1, 1);
		snakes.add(snake);
		addDrawable(snake);
		updateNodesMap(snake);
	}
	
	/**
	 * adds food during eat action
	 * @param x
	 * @param y
	 */
	public void addFood(int x, int y) {
		food = new Food(x,y);
		addDrawable(food);
		nodesMap[food.getX()][food.getY()] = food;
	}
	
	/**
	 * Removes node
	 * @param node which corresponds food
	 * Removes food during eat action
	 */
	private void removeNode(Node node) {
		if (node != null) {
			snakes.remove(node);
			removeDrawable(node);
			if (isPositionInsideGrid(node.getX(), node.getY())) {
				nodesMap[node.getX()][node.getY()] = null;
			}
		}
	}
	
	/**
	 * Creates a local information for a node 
	 * For keeping the information of the node
	 * @param node
	 * @return
	 */
	private LocalInformation createLocalInformationForNode(Node node) {
		int x = node.getX();
		int y = node.getY();
		
		HashMap<Direction, Node> snake = new HashMap<>();
		snake.put(Direction.UP, getNodeAtPosition(x, y - 1));
		snake.put(Direction.DOWN, getNodeAtPosition(x, y + 1));
		snake.put(Direction.LEFT, getNodeAtPosition(x - 1, y));
		snake.put(Direction.RIGHT, getNodeAtPosition(x + 1, y));
		
		ArrayList<Direction> freeDirections = new ArrayList<>();
		if (snake.get(Direction.UP) == null && isPositionInsideGrid(x, y - 1)) {
			freeDirections.add(Direction.UP);
		}if (snake.get(Direction.DOWN) == null && isPositionInsideGrid(x, y + 1)) {
			freeDirections.add(Direction.DOWN);
		}if (snake.get(Direction.LEFT) == null && isPositionInsideGrid(x - 1, y)) {
			freeDirections.add(Direction.LEFT);
		}if (snake.get(Direction.RIGHT) == null && isPositionInsideGrid(x + 1, y)) {
			freeDirections.add(Direction.RIGHT);
		}
		return new LocalInformation(getGridWidth(), getGridHeight(), snake, freeDirections, food);
	}
	
	/**
	 * Controls whether the position is inside of the grid or not
	 * @param x
	 * @param y
	 * @return 
	 */
	private boolean isPositionInsideGrid(int x, int y) {
		return (x >= 0 && x < getGridWidth()) && (y >= 0 && y < getGridHeight());
	}
	
	/**
	 * Updates the snake's nodes after each changes like removing the node adding the node 
	 * @param snake
	 */
	private void updateNodesMap(Snake snake) {

		for(int i = 0;i < snake.getSnakeParts().size();i++) {
			nodesMap[snake.getSnakeParts().get(i).getX()][snake.getSnakeParts().get(i).getY()] = snake.getSnakeParts().get(i);
		}
	}
	
	/**
	 * Gets the node at position
	 * @param x
	 * @param y
	 * @return
	 */
	private Node getNodeAtPosition(int x, int y) {
		if (!isPositionInsideGrid(x, y)) {
			return null;
		}
		return (Node) nodesMap[x][y];
	}
	
	/**
	 * gets the node's direction
	 * @param x
	 * @param y
	 * @param direction
	 * @return node
	 */
	private Node getNodeAtDirection(int x, int y, Direction direction) {
		int xTarget = x;
		int yTarget = y;
		
		if (direction == null) {
			return null;
		} if (direction == Direction.UP) {
			yTarget--;
		} else if (direction == Direction.DOWN) {
			yTarget++;
		} else if (direction == Direction.LEFT) {
			xTarget--;
		} else if (direction == Direction.RIGHT) {
			xTarget++;
		}
		return getNodeAtPosition(xTarget, yTarget);
	}
	
	/**
	 * Controls whether the position is free or not.
	 * @param x
	 * @param y
	 * @return
	 */
	private boolean isPositionFree(int x, int y) {
		return isPositionInsideGrid(x, y) && getNodeAtPosition(x, y) == null;
	}
	
	/**
	 * Controls whether the direction is free or not
	 * @param x
	 * @param y
	 * @param direction
	 * @return
	 */
	private boolean isDirectionFree(int x, int y, Direction direction) {
		int xTarget = x;
		int yTarget = y;
		
		if (direction == null) {
			return false;
		} if (direction == Direction.UP) {
			yTarget--;
		} else if (direction == Direction.DOWN) {
			yTarget++;
		} else if (direction == Direction.LEFT) {
			xTarget--;
		} else if (direction == Direction.RIGHT) {
			xTarget++;
		}
		return isPositionFree(xTarget, yTarget);
	}
}