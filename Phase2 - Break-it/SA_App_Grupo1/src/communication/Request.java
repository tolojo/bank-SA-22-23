package communication;

import java.io.Serializable;

public class Request implements Serializable  {

    private static final long serialVersionUID = -5425199756404304831L;

    private SignedPayload signedPayload;
	private SignedShop signedShop;
    private boolean vcc;
    
    public Request(SignedPayload signedPayload) {
        this.signedPayload = signedPayload;
        vcc = false;
    }
    
    public Request(SignedShop signedShop) {
    	this.signedShop = signedShop;
    	vcc = true;
    }

    public SignedPayload getSignedPayload() {
        return signedPayload;
    }

	public SignedShop getSignedShop() {
		return signedShop;
	}

	public boolean isVcc() {
		return vcc;
	}
    
}
