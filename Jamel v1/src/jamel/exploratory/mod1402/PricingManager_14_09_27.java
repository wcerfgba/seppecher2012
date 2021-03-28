/* =========================================================
 * JAMEL : a Java (tm) Agent-based MacroEconomic Laboratory.
 * =========================================================
 *
 * (C) Copyright 2007-2014, Pascal Seppecher and contributors.
 * 
 * Project Info <http://p.seppecher.free.fr/jamel/javadoc/index.html>. 
 *
 * This file is a part of JAMEL (Java Agent-based MacroEconomic Laboratory).
 * 
 * JAMEL is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * JAMEL is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with JAMEL. If not, see <http://www.gnu.org/licenses/>.
 *
 * [Oracle and Java are registered trademarks of Oracle and/or its affiliates.]
 * [JAMEL uses JFreeChart, copyright by Object Refinery Limited and Contributors. 
 * JFreeChart is distributed under the terms of the GNU Lesser General Public Licence (LGPL). 
 * See <http://www.jfree.org>.]
 */

package jamel.exploratory.mod1402;

import jamel.Circuit;
import jamel.agents.firms.Labels;
import jamel.agents.firms.managers.AbstractPricingManager;
import jamel.agents.firms.util.Mediator;

/**
 * A pricing manager that uses a trial and error process to find the good price, observing both sales and inventories.<p>
 * (new version of the old PricingManager131201).
 */
public class PricingManager_14_09_27 extends AbstractPricingManager {
	
	static private double price = 35;
	static private int lastUpdate = 0; 

	/**
	 * Creates a new pricing manager.
	 * @param mediator  the mediator.
	 */
	public PricingManager_14_09_27(Mediator mediator) {
		this.mediator=mediator;
	}

	/**
	 * Closes the pricing manager.<p>
	 * Calculates the sales ratio.
	 */
	@Override
	public void close() {
	}

	/* (non-Javadoc)
	 * @see java.lang.Object#toString()
	 */
	@Override
	public String toString() {
		String string = this.getClass().getCanonicalName();
		string+=", currentPrice="+currentPrice;
		return string;
	}

	/**
	 * Updates the unit price.
	 */
	@Override
	public void updatePrice() {
		final Float priceFlexibility = Float.parseFloat(Circuit.getParameter(PARAM_PRICE_FLEX));
		final int p = getCurrentPeriod().getValue();
		if (p>lastUpdate) {
			lastUpdate = p;
			price =  price*(1f+0.003);
		}
		this.currentPrice = price;
	}

	@Override
	public Object get(String key) {
		Object result=super.get(key);
		return result;
	}

}




















