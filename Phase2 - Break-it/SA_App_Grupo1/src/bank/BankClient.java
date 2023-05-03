package bank;

import java.security.Key;
import java.sql.Timestamp;

public class BankClient {
	private long balance;
	private int accountNr;
	private Key publicKey;
	private int creditcardNr = 0;
	private Timestamp lastTs;
	
	public BankClient(long balance, int accountNr, Key pK, Timestamp ts) {
		this.balance = balance;
		this.accountNr = accountNr;
		this.publicKey = pK;
		this.lastTs = ts;
	}
	
	public int getAccountNr() {
		return accountNr;
	}
	
	public boolean checkBalance(long value) {
		return balance - value >= 0;
	}
	
	public boolean withdraw(long value) {
		if(value > 0 && checkBalance(value)){
			balance -= value;
			return true;
		}
		return false;
	}
	
	public boolean deposit(long value) {
		if(value >0) {
			balance += value;
			return true;
		}
		return false;
	}
	
	public long getBalance() {
		return balance;
	}
	
	public int generateCC() {
		creditcardNr++;
		return creditcardNr;
	}

	public Key getPublicKey() {
		return publicKey;
	}

	public String getCurrentCardId() {
		return accountNr + "_" + creditcardNr;
	}
	
	public Timestamp getTimestamp() {
		return lastTs;
	}
	
	public boolean validTs(Timestamp ts) {
		return lastTs.before(ts);
	}
	
	public boolean updateTimestamp(Timestamp ts) {
		if(validTs(ts)) {
			lastTs = ts;
			return true;
		}
		return false;
	}
	
}