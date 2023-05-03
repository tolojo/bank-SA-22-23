package communication;

import java.io.Serializable;

import javax.crypto.SealedObject;

public class SealedRequest implements Serializable {
	
	private static final long serialVersionUID = -4129172315135796756L;
	
	private byte[] sessionKey;
	private SealedObject request;
	
	public SealedRequest(SealedObject request, byte[] sessionKey) {
		this.request = request;
		this.sessionKey = sessionKey;
	}
	
	public byte[] getSessionKey() {
        return sessionKey;
    }
	
	public SealedObject getRequest() {
		return request;
	}
    
}
