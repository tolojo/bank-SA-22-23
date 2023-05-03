package communication;

import java.io.Serializable;
import java.security.Key;
import java.security.PrivateKey;
import java.security.PublicKey;
import java.security.Signature;
import java.sql.Timestamp;

public class SignedShop implements Serializable {
	private static final long serialVersionUID = -8668814083583674654L;
	
	private ShoppingDetails details;
	private byte [] signature;
	
	public SignedShop(String id, long ammount, Timestamp ts,String ipClient, int portClient) {
		details = new ShoppingDetails(id, ammount,ts,  ipClient, portClient);
	}
	
	public boolean sign(Key sk) {
		try {
			Signature sign = Signature.getInstance("SHA256withRSA");
			sign.initSign((PrivateKey) sk);
			sign.update(tools.ObjectsToBytes.convertObjectToBytes(details));
			signature = sign.sign();
			return true;
		}
		catch(Exception e) {
		}
		return false;
	}
	
	public boolean verify(Key pk) {
		try {
			Signature sign = Signature.getInstance("SHA256withRSA");
			sign.initVerify((PublicKey) pk);
			sign.update(tools.ObjectsToBytes.convertObjectToBytes(details));
			return sign.verify(signature);
		}
		catch(Exception e) {
		}
		return false;
	}
	public ShoppingDetails getShoppingDetails() {
		return details;
	}
	
}
