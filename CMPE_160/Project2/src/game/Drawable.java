package game;

import ui.GridPanel;


/**
 * Interface that allows objects to be drawn on a grid panel
 */
public interface Drawable {

    /**
     * Method that is called when an object needs to be drawn on the grid panel.
     * A class implementing this method should draw itself on the given panel.
     * @param panel grid panel to draw on
     */
    void draw(GridPanel panel);
    
}
