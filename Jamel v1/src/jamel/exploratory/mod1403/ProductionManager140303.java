/* =========================================================
 * JAMEL : a Java (tm) Agent-based MacroEconomic Laboratory.
 * =========================================================
 *
 * (C) Copyright 2007-2013, Pascal Seppecher and contributors.
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
 */

package jamel.exploratory.mod1403;

import jamel.Circuit;
import jamel.agents.firms.Labels;
import jamel.agents.firms.managers.BasicProductionManager;
import jamel.agents.firms.util.Mediator;

/**
 * An interface for the production managers.
 */
public class ProductionManager140303 extends BasicProductionManager {

	@SuppressWarnings("javadoc")
	protected static final String HIGH_INVENTORY_LEVEL_RATIO = "Firms.inventories.level.high";

	@SuppressWarnings("javadoc")
	protected static final String LOW_INVENTORY_LEVEL_RATIO = "Firms.inventories.level.low";

	@SuppressWarnings("javadoc")
	private final float highInventoryLevelRatio;

	@SuppressWarnings("javadoc")
	private final float lowInventoryLevelRatio;

	@SuppressWarnings("javadoc")
	private final float utilizationRateFlexibility;

	/**
	 * Creates a new production manager.
	 * @param mediator  the mediator.
	 */
	public ProductionManager140303(Mediator mediator) {
		super(mediator);
		this.utilizationRateFlexibility = Float.parseFloat(Circuit.getParameter(PARAM_UTIL_RATE_FLEX));
		this.highInventoryLevelRatio = Float.parseFloat(Circuit.getParameter(HIGH_INVENTORY_LEVEL_RATIO));
		this.lowInventoryLevelRatio = Float.parseFloat(Circuit.getParameter(LOW_INVENTORY_LEVEL_RATIO));
	}

	/* (non-Javadoc)
	 * @see jamel.agents.firms.managers.ProductionManager#updateProductionLevel()
	 */
	@Override
	public void updateProductionLevel() {
		final float alpha1 = getRandom().nextFloat();
		final float alpha2 = getRandom().nextFloat();
		final int currentVol = (Integer) this.mediator.get(Labels.INVENTORY_FG_VOLUME);
		final int productionMaxVol = (Integer) this.mediator.get(Labels.PRODUCTION_MAX);
		final float lowTarget = this.lowInventoryLevelRatio*productionMaxVol;
		final float highTarget = this.highInventoryLevelRatio*productionMaxVol;
		//final float inventoryRatio = (Float)this.mediator.get(Labels.INVENTORY_LEVEL_RATIO);
		if (currentVol/lowTarget<1-alpha1*alpha2) {// Low level
			final float delta = (alpha1*utilizationRateFlexibility);
			this.utilizationRateTargeted += delta;
			if (this.utilizationRateTargeted>100) {
				this.utilizationRateTargeted = 100;
			}
		}
		else if (currentVol/highTarget>1+alpha1*alpha2) {// High level
			final float delta = (alpha1*utilizationRateFlexibility);
			this.utilizationRateTargeted -= delta;
			if (this.utilizationRateTargeted<0) {
				this.utilizationRateTargeted = 0;
			}
		}
		final float maxUtilization = (Float) this.mediator.get(Labels.PRODUCTION_LEVEL_MAX);
		this.utilizationRateRectified = Math.min(this.utilizationRateTargeted, maxUtilization);
	}

}