package communication;

import java.io.Serializable;

import javax.crypto.SealedObject;

public class SealedReply implements Serializable {
	private static final long serialVersionUID = -4010664286659364410L;
	
	private SealedObject reply;
	private byte[] encryptedKey;
	
	public SealedReply(SealedObject reply, byte[] encryptedKey) {
		this.encryptedKey = encryptedKey;
		this.reply = reply;
	}

	public SealedObject getReply() {
		return reply;
	}

	public byte[] getEncryptedKey() {
		return encryptedKey;
	}
}
