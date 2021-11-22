package naturesimulator;

import game.Direction;
import project.Food;
import project.Node;
import java.util.HashMap;
import java.util.List;


/**
 * Class representing the information a node has about its surroundings.
 * S
 */
public class LocalInformation {

    private int gridWidth;
    private int gridHeight;
    private Node food;
    private HashMap<Direction, Node> nodes;
    private List<Direction> freeDirections;

    /**
     * Constructs the local information for a node
     * @param Food food 
     * @param HashMap<Direction, Node> nodes keeps Nodes
     * @param gridWidth width of the grid world
     * @param gridHeight height of the grid world
     * @param nodes mapping of directions to neighbor nodes
     * @param freeDirections list of free directions
     */
    LocalInformation(int gridWidth, int gridHeight,
                     HashMap<Direction, Node> nodes, List<Direction> freeDirections, Food food) {
        this.gridWidth = gridWidth;
        this.gridHeight = gridHeight;
        this.nodes = nodes;
        this.freeDirections = freeDirections;
        this.food = food;
        
   }
    
    /**
     * getter for the food 
     * @return
     */
    public Node getFood() {
		return this.food;
	}

    /**
     * Getter for the width of the grid world.
     * Can be used to assess the boundaries of the world.
     * @return number of grid squares along the width
     */
    public int getGridWidth() {
        return gridWidth;
    }

    /**
     * Getter for the height of the grid world.
     * Can be used to assess the boundaries of the world.
     * @return number of grid squares along the height
     */
    public int getGridHeight() {
        return gridHeight;
    }

    /**
     * Returns the neighbor creature one square up
     * @return creature or null if no creature exists
     */
    public Node getCreatureUp() {
        return nodes.get(Direction.UP);
    }

    /**
     * Returns the neighbor creature one square down
     * @return creature or null if no creature exists
     */
    public Node getCreatureDown() {
        return nodes.get(Direction.DOWN);
    }

    /**
     * Returns the neighbor creature one square left
     * @return creature or null if no creature exists
     */
    public Node getCreatureLeft() {
        return nodes.get(Direction.LEFT);
    }

    /**
     * Returns the neighbor creature one square right
     * @return creature or null if no creature exists
     */
    public Node getCreatureRight() {
        return nodes.get(Direction.RIGHT);
    }

    /**
     * Returns the list of free directions around the current position.
     * The list does not contain directions out of bounds or containing a creature.
     * Can be used to determine the directions available to move or reproduce.
     * @return creature or null if no creature exists
     */
    public List<Direction> getFreeDirections() {
        return freeDirections;
    }

    /**
     * Utility function to get a randomly selected direction among multiple directions.
     * The selection is uniform random: All directions in the list have an equal chance to be chosen.
     * @param possibleDirections list of possible directions
     * @return direction randomly selected from the list of possible directions
     */
    public static Direction getRandomDirection(List<Direction> possibleDirections) {
        if (possibleDirections.isEmpty()) {
            return null;
        }
        int randomIndex = (int)(Math.random() * possibleDirections.size());
        return possibleDirections.get(randomIndex);
    }

}
