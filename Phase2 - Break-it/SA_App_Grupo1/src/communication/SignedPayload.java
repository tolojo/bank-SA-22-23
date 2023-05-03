package communication;

import java.io.Serializable;
import java.security.Key;
import java.security.PrivateKey;
import java.security.PublicKey;
import java.security.Signature;

public class SignedPayload implements Serializable {
	private static final long serialVersionUID = -5008681448876719636L;
	
	private Payload payload;
	private byte [] signature;
	
	public SignedPayload(Payload payload) {
		this.payload = payload;;
	}
	
	public boolean sign( Key sk) {
		try {
			Signature sign = Signature.getInstance("SHA256withRSA");
		    sign.initSign((PrivateKey) sk);
		    sign.update(tools.ObjectsToBytes.convertObjectToBytes(payload));
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
			sign.update(tools.ObjectsToBytes.convertObjectToBytes(payload));
			return sign.verify(signature);
		}
		catch(Exception e) {
		}
		return false;
	}

	public Payload getPayload() {
		return payload;
	}

	public byte[] getSignature() {
		return signature;
	}
}
