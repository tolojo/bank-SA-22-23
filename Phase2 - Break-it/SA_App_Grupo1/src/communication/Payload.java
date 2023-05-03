package communication;

import java.io.Serializable;
import java.security.Key;
import java.sql.Timestamp;

public class Payload implements Serializable {
	private static final long serialVersionUID = -4551047183737092216L;
	
	private OperationMode mode;
	private int account;
	private long ammount;
	private Key pk;
	private Timestamp ts;
	
	public Payload(int account, long ammount, OperationMode mode, Key pk, Timestamp ts) {
		this.account = account;
		this.ammount = ammount;
		this.mode = mode;
		this.pk = pk;
		this.ts = ts;
	}

	public OperationMode getMode() {
		return mode;
	}

	public int getAccount() {
		return account;
	}

	public long getAmmount() {
		return ammount;
	}

	public Key getPk() {
		return pk;
	}
	
	public Timestamp getTimestamp() {
		return ts;
	}
	
}