package communication;

import java.io.Serializable;
import java.sql.Timestamp;

public class ShoppingDetails implements Serializable {
	
	private static final long serialVersionUID = 3274964378690158648L;
	
	private Timestamp ts;
	private String id;
	private long ammount;
	private String ipBank;
	private int portBank;
	
	public ShoppingDetails(String id, long ammount, Timestamp ts, String ipBank, int portBank) {
		this.ammount = ammount;
		this.id = id;
		this.ipBank = ipBank;
		this.portBank = portBank;
		this.ts = ts;
	}

	public String getId() {
		return id;
	}

	public long getAmmount() {
		return ammount;
	}
	
	public Timestamp getTimestamp() {
		return ts;
	}
	
	public String getIp() {
		return ipBank;
	}
	
	public int getPort() {
		return portBank;
	}
	
}