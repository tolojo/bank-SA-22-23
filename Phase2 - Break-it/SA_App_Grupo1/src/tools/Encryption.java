package tools;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.io.Serializable;
import java.nio.file.Files;
import java.security.Key;
import java.security.KeyFactory;
import java.security.KeyPair;
import java.security.KeyPairGenerator;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.security.spec.EncodedKeySpec;
import java.security.spec.PKCS8EncodedKeySpec;
import java.security.spec.X509EncodedKeySpec;
import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SealedObject;
import javax.crypto.SecretKey;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.IvParameterSpec;
import javax.crypto.spec.PBEKeySpec;
import javax.crypto.spec.PBEParameterSpec;
import javax.crypto.spec.SecretKeySpec;

import communication.VccStoredFile;

public class Encryption {

	private Encryption() {}
	
	public static KeyPair generateKeyPair() {
		try {
			KeyPairGenerator generator = KeyPairGenerator.getInstance("RSA");
			generator.initialize(4096);
			
			return generator.generateKeyPair();
		} catch (NoSuchAlgorithmException e) {
			return null;
		}
	}
	
	public static Key generateKey() {
		try {
			KeyGenerator generator = KeyGenerator.getInstance("AES");
			generator.init(128);
			return generator.generateKey();
		} catch (NoSuchAlgorithmException e) {
			return null;
		}
	}
	
	public static boolean storeKeyInFile(Key key, String fileName) { //return false if IOException or file already exists
		try {
			File file = new File(fileName);
			
			if(file.createNewFile()) { // creates file if it does not exist
				FileOutputStream fos = new FileOutputStream(file);
				fos.write(key.getEncoded());
				fos.close();
				return true;
			}
		} catch (IOException e) {
		}
		
		return false;
	}
	
	public static Key retrieveKeyFromFile(String fileName, boolean isPublicKey) { //return false if file does not exists
		
		try {
			File file = new File(fileName);
			
			if(file.canRead()) {
				byte[] keyBytes = Files.readAllBytes(file.toPath());
				
				KeyFactory keyFactory = KeyFactory.getInstance("RSA");
				
				if(isPublicKey) {
					EncodedKeySpec keySpec = new X509EncodedKeySpec(keyBytes);
					return keyFactory.generatePublic(keySpec);
				} else {
					EncodedKeySpec keySpec = new PKCS8EncodedKeySpec(keyBytes);
					return keyFactory.generatePrivate(keySpec);
				}
			}
		} catch (Exception e) {
		}
		
		return null;
	}
	
	public static byte [] encryptRSA(Key key, Key keyToCipher) {

		try {
			Cipher encryptCipher = Cipher.getInstance("RSA");
			encryptCipher.init(Cipher.ENCRYPT_MODE, key);
			return encryptCipher.doFinal(keyToCipher.getEncoded());
			
		} catch (Exception e) {
			return null;
		}
		
	}
	
	public static Object decryptRSA(Key key, byte [] object) {
		try {
			Cipher decryptCipher = Cipher.getInstance("RSA");
			decryptCipher.init(Cipher.DECRYPT_MODE, key);
			byte [] bytes = decryptCipher.doFinal(object);
			
			return new SecretKeySpec(bytes, 0, bytes.length, "AES");
		} catch (Exception e) {
			return null;
		}
	}
	
	public static SealedObject encryptAES(Key key, Serializable object) {

		try {
			Cipher encryptCipher = Cipher.getInstance("AES");
			encryptCipher.init(Cipher.ENCRYPT_MODE, key);
			return new SealedObject(object, encryptCipher);
			
		} catch (Exception e) {
			return null;
		}	
	}
	
	public static Object decryptAES(Key key, SealedObject object) {
		try {
			return object.getObject(key);
			
		} catch (Exception e) {
			return null;
		}
	}
	
	public static boolean createVcc(VccStoredFile vcc, String filename, String password) {
		try {
			
			FileOutputStream outFile = new FileOutputStream(filename);
			ObjectOutputStream outStream = new ObjectOutputStream(outFile);
	
			PBEKeySpec pbeKeySpec = new PBEKeySpec(password.toCharArray());
			SecretKeyFactory secretKeyFactory = SecretKeyFactory
					.getInstance("PBEWithHmacSHA256AndAES_128");
			SecretKey secretKey = secretKeyFactory.generateSecret(pbeKeySpec);
	
			byte[] salt = new byte[8];
			SecureRandom random = new SecureRandom();
			random.nextBytes(salt);
			
			byte[] iv = new byte[16];
			random.nextBytes(iv);
	
			PBEParameterSpec pbeParameterSpec = new PBEParameterSpec(salt, 100, new IvParameterSpec(iv));
			Cipher cipher = Cipher.getInstance("PBEWithHmacSHA256AndAES_128");
			cipher.init(Cipher.ENCRYPT_MODE, secretKey, pbeParameterSpec);
			
			outStream.writeObject(salt);
			outStream.writeObject(cipher.getIV());
	
			SealedObject obj = new SealedObject(vcc, cipher);
			
			outStream.writeObject(obj);
	
			outStream.flush();
			outStream.close();
			
			return true;
		} catch(Exception e) {
			return false;
		}
		
	}
	
	public static VccStoredFile retrieveVcc(String filename, String password) {
		
		try {
			PBEKeySpec pbeKeySpec = new PBEKeySpec(password.toCharArray());
			SecretKeyFactory secretKeyFactory = SecretKeyFactory
					.getInstance("PBEWithHmacSHA256AndAES_128");
			SecretKey secretKey = secretKeyFactory.generateSecret(pbeKeySpec);
	
			FileInputStream fis = new FileInputStream(filename);
			ObjectInputStream inStream = new ObjectInputStream(fis);
			byte[] salt = (byte[]) inStream.readObject();
			byte[] iv = (byte[]) inStream.readObject();
	
			PBEParameterSpec pbeParameterSpec = new PBEParameterSpec(salt, 100, new IvParameterSpec(iv));
	
			Cipher cipher = Cipher.getInstance("PBEWithHmacSHA256AndAES_128");
			cipher.init(Cipher.DECRYPT_MODE, secretKey, pbeParameterSpec);

			SealedObject obj = (SealedObject) inStream.readObject();
			inStream.close();
			
			return (VccStoredFile) obj.getObject(cipher);
		
		} catch(Exception e) {
			return null;
		}
		
	}
}