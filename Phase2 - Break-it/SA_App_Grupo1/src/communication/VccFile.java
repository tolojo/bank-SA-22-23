package communication;

import java.io.Serializable;
import java.security.Key;

public class VccFile implements Serializable {
	private static final long serialVersionUID = 2948818280210873678L;
	
	private String Id;
	private String reply;
	private Key key;
	
	public VccFile(String Id, String reply, Key key) {
		this.Id = Id;
		this.reply = reply;
		this.key = key;
	}

	public String getId() {
		return Id;
	}

	public String getReply() {
		return reply;
	}

	public Key getKey() {
		return key;
	}
	
}
