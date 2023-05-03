package bank;

import java.security.Key;

public class Vcc {
	private Key key;
	private long ammount;
	private String id;
	private int account;
	private boolean active = true;
	
	public Vcc(int account, long ammount, Key key, String id) {
		this.account = account;
		this.ammount = ammount;
		this.key = key;
		this.id = id;
	}

	public boolean isActive() {
		return active;
	}

	public void use() {
		active = false;
	}

	public int getAccount() {
		return account;
	}

	public String getId() {
		return id;
	}

	public long getAmmount() {
		return ammount;
	}

	public Key getKey() {
		return key;
	}
	
}
