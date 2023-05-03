package store;

import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.net.Socket;
import java.security.Key;

import javax.crypto.SealedObject;

import communication.Request;
import communication.SealedRequest;
import tools.Encryption;

public class StoreThread extends Thread{

	 private Socket clientSocket;
	 private String authFile;
	 private String bankIp;
	 private int bankPort;

     public StoreThread(Socket inSoc, String authFile) {
    	 clientSocket = inSoc;
    	 this.authFile = authFile;
     }
     
     public void run(){
    	 
    	 ObjectOutputStream oosClient = null;
    	 ObjectInputStream oisClient = null;
    	 ObjectOutputStream oosBank = null;
    	 ObjectInputStream oisBank = null;
    	 
    		 if(clientSocket != null) {
	    		 try {
	    			 oosClient = new ObjectOutputStream(clientSocket.getOutputStream());
		             oisClient = new ObjectInputStream(clientSocket.getInputStream());
		            
		             Object received = oisClient.readObject();
		             Request request = (Request) received;
		             bankIp =request.getSignedShop().getShoppingDetails().getIp();
		             bankPort = request.getSignedShop().getShoppingDetails().getPort();
		            
		             Socket bankSocket = new Socket(bankIp, bankPort);
		             
		             oosBank = new ObjectOutputStream(bankSocket.getOutputStream());
		             oisBank = new ObjectInputStream(bankSocket.getInputStream());
		             
		             Key bankPublicKey = Encryption.retrieveKeyFromFile(authFile, true);
		     		 Key sessionKey = Encryption.generateKey();
		     		
		     		 byte[] encryptedKey = Encryption.encryptRSA(bankPublicKey, sessionKey);
		     		 SealedObject sealedObj = Encryption.encryptAES(sessionKey, request);
		     		 SealedRequest sealedRequest = new SealedRequest(sealedObj, encryptedKey);
		            
		             oosBank.writeObject(sealedRequest);
		             
		             Object bankReply = oisBank.readObject();
		             SealedObject sealedObjToStore = (SealedObject) oisBank.readObject();
		             String reply = (String) Encryption.decryptAES(sessionKey, sealedObjToStore);
		             
		             if(!reply.equals("ERROR")) {
		            	 System.out.println(reply);
			             System.out.flush();
		             }
		             oosClient.writeObject(bankReply);
		             
		             oosBank.close();
	            	 oisBank.close();
	            	 oosClient.close();
	            	 oisClient.close();
	            	 bankSocket.close();
		            
	    		 }
	    		 catch (Exception e) {
		          }
    		 }
     }  
 
}
