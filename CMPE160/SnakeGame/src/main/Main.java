package main;

import project.Food;
import project.Snake;
import ui.ApplicationWindow;
import java.awt.*;
import naturesimulator.SnakesGameSimulator;

/**
 * The main class that can be used as a playground to test your project.
 */
public class Main {

    /**
     * Main entry point for the application.
     * @param args application arguments
     */
    public static void main(String[] args) {
        EventQueue.invokeLater(() -> {
            try {
         // Create game
         // You can change the world width and height, size of each grid square in pixels or the game speed
            	SnakesGameSimulator game = new SnakesGameSimulator(70, 40, 20, 70);

                	int x = (int) (Math.random() * game.getGridWidth());
				int y = (int) (Math.random() * game.getGridHeight());
				//	if the coordinates are the first snake's coordinates, it loops till it gets an available empty coordinate
				while(y==1) {
					if(x==1) {
					 x = (int) (Math.random() * game.getGridWidth());
					 y = (int) (Math.random() * game.getGridHeight());
					}else if(x==2) {
					 x = (int) (Math.random() * game.getGridWidth());
					 y = (int) (Math.random() * game.getGridHeight());
					}else if(x==3) {
				     x = (int) (Math.random() * game.getGridWidth());
				     y = (int) (Math.random() * game.getGridHeight());
					}else if(x==4) {
					 x = (int) (Math.random() * game.getGridWidth());
					 y = (int) (Math.random() * game.getGridHeight());
					}else {
						
						game.addFood(x, y);
					}
				}
				// adds the food into the null node
				game.addFood(x, y); 
				
				// adds snake
                game.addSnake();
                // Create application window that contains the game panel
                ApplicationWindow window = new ApplicationWindow(game.getGamePanel());
                window.getFrame().setVisible(true);
                
                // Start game
                game.start();

            } catch (Exception e) {
                e.printStackTrace();
            }
        });
    }
}
