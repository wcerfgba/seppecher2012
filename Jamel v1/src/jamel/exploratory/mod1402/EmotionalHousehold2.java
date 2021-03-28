package jamel.exploratory.mod1402;

import jamel.Circuit;

/**
 * Une extension d'EmotionalHousehold dont le comportement de fixation du salaire de réserve dépend du moral.
 * Créé le 26 mars 2014, pour tester les effets de ménages plus flexibles en temps de crise.
 */
public class EmotionalHousehold2 extends EmotionalHousehold {

	@SuppressWarnings("javadoc")
	protected final String PARAM_WAGE_FLEX2 = "Households.wage.flexibility2";

	@SuppressWarnings("javadoc")
	protected final String PARAM_WAGE_RESIST2 = "Households.wage.resistance2";

	/**
	 * Creates a new household.
	 * @param aName  the name of the household.
	 */
	public EmotionalHousehold2(String aName) {
		super(aName);
	}

	/* (non-Javadoc)
	 * @see jamel.agents.households.BasicHousehold#open()
	 */
	@Override
	public void open() {
		super.open();
		this.updateWageBehavior();
	}

	/**
	 * Updates the wage behavior according to confidence. 
	 */
	private void updateWageBehavior() {
		if (!this.newOptimist) {
			this.flexibility = Float.parseFloat(Circuit.getParameter(PARAM_WAGE_FLEX2));
			this.resistance = Float.parseFloat(Circuit.getParameter(PARAM_WAGE_RESIST2));;
		}		
	}

	
	/**
	 * Updates the reservation wage.<br>
	 * The level of the reservation wage depends on the number of periods spent in a state of unemployment.
	 * After a certain time, the unemployed worker accepts to lower its reservation wage.
	 */
	protected void updateReservationWage() {
		if (this.jobContract!=null) {							
			this.unemploymentDuration=0;					 
			this.reservationWage=this.jobContract.getWage();
			this.data.employmentDuration=getCurrentPeriod().getValue()-this.jobContract.getStart().getValue();
		}
		else {
			if (this.unemploymentDuration == 0) this.unemploymentDuration = getRandom().nextFloat() ;
			else this.unemploymentDuration += 1 ;
			final float alpha1 = getRandom().nextFloat();
			final float alpha2 = getRandom().nextFloat();
			if (alpha1*this.resistance < this.unemploymentDuration) {
				this.reservationWage=(this.reservationWage*(1f-this.flexibility*alpha2));
				/*if (this.newOptimist) {
					System.out.println(this.newOptimist);
				};*/
			}
			this.data.employmentDuration=0;
		}
		this.data.setReservationWage(this.reservationWage);
		this.data.setUnemploymentDuration(this.unemploymentDuration);
	}
	
}
