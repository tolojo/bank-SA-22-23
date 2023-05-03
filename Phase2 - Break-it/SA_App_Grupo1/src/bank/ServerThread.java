package bank;

import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.net.Socket;
import java.net.SocketTimeoutException;
import java.security.Key;
import java.security.KeyPair;
import java.sql.Timestamp;
import java.util.HashMap;
import javax.crypto.SealedObject;
import communication.Request;
import communication.SealedReply;
import communication.SealedRequest;
import communication.SignedPayload;
import communication.SignedShop;
import communication.VccFile;
import tools.Encryption;
import tools.Input;

public class ServerThread extends Thread {

	private Socket socket;
	private KeyPair kp;
	private HashMap<Integer, BankClient> clients;
	private HashMap<String, Vcc> vccs;

	public ServerThread(Socket inSoc, KeyPair kp, HashMap<Integer, BankClient> clients, HashMap<String, Vcc> vccs) {
		this.socket = inSoc;
		this.kp = kp;
		this.clients = clients;
		this.vccs = vccs;
	}

	@Override
	public void run() {
		ObjectInputStream ois = null;
		ObjectOutputStream oos = null;
		Key sessionKey = null;
		try {
			ois = new ObjectInputStream(socket.getInputStream());
			oos = new ObjectOutputStream(socket.getOutputStream());

			SealedRequest sealedRequest = (SealedRequest) ois.readObject();

			sessionKey = (Key) Encryption.decryptRSA(kp.getPrivate(), sealedRequest.getSessionKey());

			Request request = (Request) Encryption.decryptAES(sessionKey, sealedRequest.getRequest());

			if (request.isVcc()) {
				SignedShop signedShop = request.getSignedShop();
				if (vccs.containsKey(signedShop.getShoppingDetails().getId())) {
					Vcc vcc = vccs.get(signedShop.getShoppingDetails().getId());
					if (signedShop.verify(vcc.getKey()) && vcc.isActive()) {
						BankClient bc = clients.get(vcc.getAccount());
						if (bc.validTs(signedShop.getShoppingDetails().getTimestamp()) && validTimestamp(signedShop.getShoppingDetails().getTimestamp()) 
								&& Input.isMoneyLongValid(signedShop.getShoppingDetails().getAmmount(), 0, false)
								&& signedShop.getShoppingDetails().getAmmount() <= vcc.getAmmount()
								&& bc.withdraw(signedShop.getShoppingDetails().getAmmount())) {
								vcc.use();
								vccs.remove(vcc.getId());
								BankClient bc_new = bc;
								bc_new.updateTimestamp(signedShop.getShoppingDetails().getTimestamp());
								clients.replace(bc.getAccountNr(), bc, bc_new);
								String reply = "{\"vcc_file\":\"" + request.getSignedShop().getShoppingDetails().getId()
										+ "\",\"vcc_amount_used\":"
										+ Input.longAsMoney(request.getSignedShop().getShoppingDetails().getAmmount() )+ "}";
	
								Key secretKey = Encryption.generateKey();
	
								byte[] encryptedKey = Encryption.encryptRSA(vcc.getKey(), secretKey);
								SealedObject sealedObj = Encryption.encryptAES(secretKey, reply);
								SealedReply sealedReply = new SealedReply(sealedObj, encryptedKey);
								oos.writeObject(sealedReply);
								
								SealedObject sealedObjToStore = Encryption.encryptAES(sessionKey, reply);
								oos.writeObject(sealedObjToStore);
								
								System.out.println(reply);
								System.out.flush();
						}
						String replyErrorShop = "ERROR";
						SealedObject objErrorShop = Encryption.encryptAES(sessionKey, replyErrorShop);
						oos.writeObject(objErrorShop);
						oos.writeObject(objErrorShop);
						return;
					}

				}
				String replyErrorShop = "ERROR";
				SealedObject objErrorShop = Encryption.encryptAES(sessionKey, replyErrorShop);
				oos.writeObject(objErrorShop);
				oos.writeObject(objErrorShop);
			} else {

				SignedPayload signedPayload = request.getSignedPayload();
				
				switch (signedPayload.getPayload().getMode()) {

				case NEW:

					if (addUser(signedPayload.getPayload().getAccount(), signedPayload.getPayload().getAmmount(),
							signedPayload.getPayload().getPk(), signedPayload.getPayload().getTimestamp())) {
						String reply = "{\"account\":\"" + signedPayload.getPayload().getAccount()
								+ "\",\"initial_balance\":" +  Input.longAsMoney(signedPayload.getPayload().getAmmount()) + "}";
						
						SealedObject obj = Encryption.encryptAES(sessionKey, reply);
						oos.writeObject(obj);
						System.out.println(reply);
						System.out.flush();
					} else {
						String reply = "ERROR";
						SealedObject obj = Encryption.encryptAES(sessionKey, reply);
						oos.writeObject(obj);
						System.out.println("protocol_error");
						System.out.flush();
					}
					break;

				case DEPOSIT:

					if (clients.containsKey(signedPayload.getPayload().getAccount())) {
						BankClient bc = clients.get(signedPayload.getPayload().getAccount());

						if (signedPayload.verify(bc.getPublicKey()) && bc.validTs(signedPayload.getPayload().getTimestamp()) 
								&& validTimestamp(signedPayload.getPayload().getTimestamp())  && signedPayload.getPayload().getAmmount() > 0
								&& Input.isMoneyLongValid(signedPayload.getPayload().getAmmount(), 0, false)) {
							BankClient bc_new = bc;
							bc_new.updateTimestamp(signedPayload.getPayload().getTimestamp());
							bc_new.deposit(signedPayload.getPayload().getAmmount());
							clients.replace(signedPayload.getPayload().getAccount(), bc, bc_new);

							String reply = "{\"account\":\"" + signedPayload.getPayload().getAccount()
									+ "\",\"deposit\":" + Input.longAsMoney(signedPayload.getPayload().getAmmount()) + "}";
							SealedObject obj = Encryption.encryptAES(sessionKey, reply);
							oos.writeObject(obj);
							System.out.println(reply);
							System.out.flush();
							break;
						}
					}
					String reply = "ERROR";
					SealedObject obj = Encryption.encryptAES(sessionKey, reply);
					oos.writeObject(obj);
					System.out.println("protocol_error");
					System.out.flush();
					break;

				case CREATE_VCC: // OPTION

					if (clients.containsKey(signedPayload.getPayload().getAccount())) {
						BankClient bc = clients.get(signedPayload.getPayload().getAccount());
						if (signedPayload.verify(bc.getPublicKey()) && signedPayload.getPayload().getAmmount() > 0
								&& Input.isMoneyLongValid(signedPayload.getPayload().getAmmount(), 0, false)
								&& bc.validTs(signedPayload.getPayload().getTimestamp())
								&& validTimestamp(signedPayload.getPayload().getTimestamp()) 
								&& bc.checkBalance(signedPayload.getPayload().getAmmount())
								&& !vccs.containsKey(bc.getCurrentCardId())) {
							
							KeyPair vccKeys = Encryption.generateKeyPair();
							String cardID = signedPayload.getPayload().getAccount() + "_"
									+ clients.get(signedPayload.getPayload().getAccount()).generateCC();
							
							Vcc vcc = new Vcc(signedPayload.getPayload().getAccount(),
									signedPayload.getPayload().getAmmount(), vccKeys.getPublic(), cardID);
							
							vccs.put(cardID, vcc);
							
							BankClient bc_new = bc;
							bc_new.updateTimestamp(signedPayload.getPayload().getTimestamp());
							clients.replace(bc.getAccountNr(), bc, bc_new);
							
							String replyVCC = "{\"account\":\"" + signedPayload.getPayload().getAccount()
									+ "\",\"vcc_amount\":" + Input.longAsMoney(signedPayload.getPayload().getAmmount())
									+ "\",\"vcc_file\":" + cardID + ".card" + "}";
							
							VccFile vccFile = new VccFile(cardID, replyVCC, vccKeys.getPrivate());

							SealedObject objVCC = Encryption.encryptAES(sessionKey, vccFile);
							oos.writeObject(objVCC);
							System.out.println(replyVCC);
							System.out.flush();
							break;
						}
					}
					oos.writeObject(null);
					String replyError = "ERROR";
					SealedObject objError = Encryption.encryptAES(sessionKey, replyError);
					oos.writeObject(objError);
					System.out.println("protocol_error");
					System.out.flush();
					break;

				case GET: // OPTION

					if (clients.containsKey(signedPayload.getPayload().getAccount())) {
						BankClient bc = clients.get(signedPayload.getPayload().getAccount());
						if (signedPayload.verify(bc.getPublicKey()) && bc.validTs(signedPayload.getPayload().getTimestamp())
								&& validTimestamp(signedPayload.getPayload().getTimestamp()) ) {
							BankClient bc_new = bc;
							bc_new.updateTimestamp(signedPayload.getPayload().getTimestamp());
							clients.replace(bc.getAccountNr(), bc, bc_new);								
							String replyGet = "{\"account\":\"" + signedPayload.getPayload().getAccount()
									+ "\",\"balance\":" + Input.longAsMoney(bc.getBalance()) + "}";
							SealedObject objGet = Encryption.encryptAES(sessionKey, replyGet);
							oos.writeObject(objGet);
							System.out.println(replyGet);
							System.out.flush();
							break;
						}
					}
					String replyErrorGet = "ERROR";
					SealedObject objErrorGet = Encryption.encryptAES(sessionKey, replyErrorGet);
					oos.writeObject(objErrorGet);
					System.out.println("protocol_error");
					System.out.flush();
					break;
				default:
					// NOTHING IS DONE
					break;
				}
			}
		}
		catch(SocketTimeoutException st){
			System.out.println("protocol_error");
			System.out.flush();
			return;
		}
		catch (Exception e) {
			try {
				String reply = "ERROR";
				SealedObject obj = Encryption.encryptAES(sessionKey, reply);
				oos.writeObject(obj);
				System.out.println("protocol_error");
				System.out.flush();
			} catch (Exception ee) {

			}
		}
	}

	private boolean addUser(int accountNr, long balance, Key pK, Timestamp ts) {

		if (!clients.containsKey(accountNr)) {
			if (Input.isMoneyLongValid(balance, 1500, true)) {
				clients.put(accountNr, new BankClient(balance, accountNr, pK, ts));
				return true;
			}
		}
		return false;
	}
	
	private boolean validTimestamp(Timestamp ts) {
		Timestamp ats = new Timestamp(System.currentTimeMillis());
		
		return ats.after(ts);
	}
}
