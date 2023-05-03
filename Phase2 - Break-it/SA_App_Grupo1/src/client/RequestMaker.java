package client;

import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.net.Socket;
import java.net.SocketTimeoutException;
import java.security.Key;
import java.security.KeyPair;
import java.sql.Timestamp;
import java.util.Scanner;

import javax.crypto.SealedObject;

import communication.OperationMode;
import communication.Payload;
import communication.Request;
import communication.SealedReply;
import communication.SealedRequest;
import communication.SignedPayload;
import communication.SignedShop;
import communication.VccFile;
import communication.VccStoredFile;
import tools.Encryption;

public class RequestMaker {
	
	private Socket socket;
	private ObjectOutputStream outStream;
	private ObjectInputStream inStream;
	
	public RequestMaker() {}
	
	public void requestNew(int account, String authFile, String address, int port, String userFile, long amount) {
		openConnection(address, port);
		
		KeyPair pair = Encryption.generateKeyPair();
		Key sessionKey = Encryption.generateKey();
		
		Key bankPublicKey = Encryption.retrieveKeyFromFile(authFile, true);
		
		byte[] encryptedKey = Encryption.encryptRSA(bankPublicKey, sessionKey);
		
		Timestamp ts = new Timestamp (System.currentTimeMillis());
		
		Payload payload = new Payload(account, amount, OperationMode.NEW, pair.getPublic(), ts);
		SignedPayload signedPayload = new SignedPayload(payload);
		signedPayload.sign(pair.getPrivate());
		
		Request request = new Request(signedPayload);
		
		SealedObject sealedObj = Encryption.encryptAES(sessionKey, request);
		
		SealedRequest sealedRequest = new SealedRequest(sealedObj, encryptedKey);
		
		try {
			
			outStream.writeObject(sealedRequest);
			
			String reply = (String) Encryption.decryptAES(sessionKey, (SealedObject) inStream.readObject());
			
			if(reply.equals("ERROR"))
				System.exit(130);
			
			Encryption.storeKeyInFile(pair.getPrivate(), userFile);			
			System.out.println(reply);
			System.out.flush();
			
		} catch (Exception e) {
			System.exit(130);
		}		
	}
	
	public void requestDeposit(int account, String authFile, String address, int port, String userFile, long amount) {
		openConnection(address, port);
		
		
		Key bankPublicKey = Encryption.retrieveKeyFromFile(authFile, true);
		Key privateKey = Encryption.retrieveKeyFromFile(userFile, false);
		Key sessionKey = Encryption.generateKey();
		
		byte[] encryptedKey = Encryption.encryptRSA(bankPublicKey, sessionKey);
		
		Timestamp ts = new Timestamp (System.currentTimeMillis());
		
		Payload payload = new Payload(account, amount, OperationMode.DEPOSIT, null, ts);
		SignedPayload signedPayload = new SignedPayload(payload);
		signedPayload.sign(privateKey);
		
		Request request = new Request(signedPayload);
		
		SealedObject sealedObj = Encryption.encryptAES(sessionKey, request);
		
		SealedRequest sealedRequest = new SealedRequest(sealedObj, encryptedKey);
		
		try {
			outStream.writeObject(sealedRequest);
			
			String reply = (String) Encryption.decryptAES(sessionKey, (SealedObject) inStream.readObject());
			
			if(reply.equals("ERROR"))
				System.exit(130);
			
			System.out.println(reply);
			System.out.flush();
			
		} catch (IOException | ClassNotFoundException e) {
			System.exit(130);
		}
	}
	
	public void requestGet(int account, String authFile, String address, int port, String userFile) {
		openConnection(address, port);
		
		Key bankPublicKey = Encryption.retrieveKeyFromFile(authFile, true);
		Key privateKey = Encryption.retrieveKeyFromFile(userFile, false);
		Key sessionKey = Encryption.generateKey();
		
		byte[] encryptedKey = Encryption.encryptRSA(bankPublicKey, sessionKey);
		
		Timestamp ts = new Timestamp (System.currentTimeMillis());
		
		Payload payload = new Payload(account, -1, OperationMode.GET, null, ts);
		SignedPayload signedPayload = new SignedPayload(payload);
		signedPayload.sign(privateKey);
		
		Request request = new Request(signedPayload);
		
		SealedObject sealedObj = Encryption.encryptAES(sessionKey, request);
		
		SealedRequest sealedRequest = new SealedRequest(sealedObj, encryptedKey);
		
		try {
			outStream.writeObject(sealedRequest);
			
			String reply = (String) Encryption.decryptAES(sessionKey, (SealedObject) inStream.readObject());
			
			if(reply.equals("ERROR"))
				System.exit(130);
			
			System.out.println(reply);
			System.out.flush();
			
		} catch (IOException | ClassNotFoundException e) {
			System.exit(130);
		}
	}
	
	public void requestVcc(int account, String authFile, String address, int port, String userFile, long amount) {
		openConnection(address, port);
		
		Key bankPublicKey = Encryption.retrieveKeyFromFile(authFile, true);
		Key privateKey = Encryption.retrieveKeyFromFile(userFile, false);
		Key sessionKey = Encryption.generateKey();
		
		byte[] encryptedKey = Encryption.encryptRSA(bankPublicKey, sessionKey);
		
		Timestamp ts = new Timestamp (System.currentTimeMillis());
		
		Payload payload = new Payload(account, amount, OperationMode.CREATE_VCC, null, ts);
		SignedPayload signedPayload = new SignedPayload(payload);
		signedPayload.sign(privateKey);
		
		Request request = new Request(signedPayload);
		
		SealedObject sealedObj = Encryption.encryptAES(sessionKey, request);
		
		SealedRequest sealedRequest = new SealedRequest(sealedObj, encryptedKey);
		
		try {
			outStream.writeObject(sealedRequest);
			
			VccFile replyVcc = (VccFile) Encryption.decryptAES(sessionKey, (SealedObject) inStream.readObject());
			
			VccStoredFile vccStored = new VccStoredFile(replyVcc.getKey(), address, port);
			
			System.out.println("Insert your pin code:");
			System.out.flush();
			Scanner s = new Scanner (System.in);
			String password = s.nextLine();
			s.close();
			Encryption.createVcc(vccStored, replyVcc.getId() + ".card", password);
			
			if(replyVcc.getReply().equals("ERROR"))
				System.exit(130);
			
			System.out.println(replyVcc.getReply());
			System.out.flush();
			
		} catch (Exception e) {
			System.exit(130);
		}
	}
	
	public void requestShop(String address, int port, String vccFile, long amount, Timestamp ts) {
		openConnection(address, port);
		
		if(vccFile == null) {
			System.exit(130);
		}
		
		System.out.println("Insert your pin code:");
		System.out.flush();
		Scanner s = new Scanner (System.in);
		String password = s.nextLine();
		s.close();
		VccStoredFile vccStored = Encryption.retrieveVcc(vccFile, password);
		
		if(vccStored == null) {
			System.out.println("Wrong pin");
			System.out.flush();
			System.exit(130);
		}
		
		Key privateKey = vccStored.getKey();
		
		if(privateKey == null) {
			System.exit(130);
		}
		
		SignedShop signedShop = new SignedShop(vccFile.split("\\.")[0], amount, ts, vccStored.getBankIp(), vccStored.getBankPort());
		signedShop.sign(privateKey);
		
		Request r = new Request(signedShop);
		
		try {
			outStream.writeObject(r);
			
			System.out.println();
			SealedReply sealedReply = (SealedReply) inStream.readObject();
			
			Key secretKey = (Key) Encryption.decryptRSA(privateKey, sealedReply.getEncryptedKey());
			
			System.out.println((String) Encryption.decryptAES(secretKey, sealedReply.getReply()));
			System.out.flush();
			
		} catch (Exception e) {
			System.exit(130);
		}
		
	}
	
	private void openConnection(String address, int port) {
		try {
			socket = new Socket(address, port);
			socket.setSoTimeout(10000);
			outStream = new ObjectOutputStream(socket.getOutputStream());
        	inStream = new ObjectInputStream(socket.getInputStream());
			
		}
		catch(SocketTimeoutException st) {
			System.exit(63);
		}
		catch (Exception e) {
			System.exit(130);
		}
	}
	
	
}
