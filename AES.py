import tkinter as tk
from tkinter import messagebox

class Application(tk.Frame):
    
    def __init__(self, master):
        super().__init__(master,width=1000,height=500)
        self.master = master
        self.pack()
        self.setup()
        self.create_widgets()
        self.roundkeys = []
        
    def setup(self):
        self.generateSBox()
        self.generateInverseSBox()

    def generateSBox(self):
       
        self.SBox = []
        row = []
        val = ""
        index = 0

        with open("AESSBox.txt", "r") as cypher_file:
            for line in cypher_file:
                line_stripped = line.replace("\t","")
             
               
                val += line_stripped[0]
               

                for i in range(1,len(line_stripped)):
                    if i % 2 == 0:
                        row.append(val)
                        val = ""
                        val += line_stripped[i].strip()
                    else:
                        val += line_stripped[i]

                
                self.SBox.append(row)
                row = []
                index = index+1
        
    def generateInverseSBox(self):
        
        
        self.InverseSBox = []
        row = []
        val = ""
        index = 0

        with open("InverseAESSBox.txt", "r") as cypher_file:
            for line in cypher_file:
                line_stripped = line.replace("\t","")
             
               
                val += line_stripped[0]
               

                for i in range(1,len(line_stripped)):
                    if i % 2 == 0:
                        row.append(val)
                        val = ""
                        val += line_stripped[i].strip()
                    else:
                        val += line_stripped[i]

                
                self.InverseSBox.append(row)
                row = []
                index = index+1
       

    def create_widgets(self):
        
        
        #Add my textbox
        self.userInputTxt = tk.Entry(self,width=100)

        self.userInputTxt.pack(pady=5,padx=10)

        #Add my buttons here
        self.encryptBtn = tk.Button(self,
                                    text = "Encrypt Password",
                                    width=100,
                                    command=self.encrypt)

        self.encryptBtn.pack(pady=5,padx=10)

        self.decryptBtn = tk.Button(self, 
                                    text = "Decrypt Password" , 
                                    width=100 , 
                                    command=self.decrypt)

        self.decryptBtn.pack(pady=5,padx=10)

        self.quitBtn = tk.Button(self, 
                                 text="QUIT", 
                                 width = 100, 
                                 fg="red", 
                                 command=self.master.destroy)

        self.quitBtn.pack(pady=5,padx=10)

    def findRoundKey(self, roundKey , round):
        

        rcon = ["1", "2" , "4" , "8" , "10" , "20" , "40" , "80" , "1b" , "36"]
        
        #matrix columns
        c0 = roundKey[0:4]
        c1 = roundKey[4:8]
        c2 = roundKey[8:12]  
        c3 = roundKey[12:16]
        
        lastColumn = roundKey[12:16]

        c4 = [0] * 4
        c5 = [0] * 4
        c6 = [0] * 4
        c7 = [0] * 4
        

        #circular byte left shift of last column
        lastColumn.append(lastColumn.pop(0))

        #Substitute values from last column with S-Box
        lastColumn = self.substitution(lastColumn, False)
         
        #adding round constant
        lastColumn[0] = self.XOR(lastColumn[0] , rcon[round] , 16)
        
        #find the round key
        for i in range(0,4):
            c4[i] = self.XOR(c0[i],lastColumn[i] , 16)
            c5[i] = self.XOR(c4[i],c1[i] , 16)
            c6[i] = self.XOR(c5[i],c2[i] , 16)
            c7[i] = self.XOR(c6[i],c3[i] , 16)

   
        return c4+c5+c6+c7
    
    
    def XOR(self, byte1, byte2, base):
        
        #use xor 
        newByte = int(byte1,base) ^ int(byte2,base)

        #reduce it to a byte
        newByte = self.reduceToByte(newByte)

        #return val
        return newByte
        

    def reduceToByte(self, bits):
        
        hexVal = hex(bits).split('x')[-1]
        b = bin(bits).split('b')[-1]
        mod = "100011011"

        while(len(b) > 8):
            overflow = b[9:]
            b = self.XOR(b[0:9],mod , 2)
            hexVal = b
            b = bin(int(hexVal,16)).split('b')[-1] + overflow

        return hexVal

    def encrypt(self):

        #set up variables
        w0 = []
        w1 = []
        w2 = []
        w3 = []
        roundKey = []
        stateMatrix = []
        fixedMatrix = [["02","01" , "01" , "03"] , ["03" , "02" , "01" , "01"] , ["01", "03" , "02" , "01"] , ["01" , "01" , "03" , "02"]]
        maxLength = 16
        messageLength = len(self.userInputTxt.get())
        message = self.userInputTxt.get()
        key = "Thats my Kung Fu"
        keyLength = len(key)


        #message is less than 16 characters
        if messageLength <= maxLength:



            #turn message and key into hexadecimal
            for i in range(0,maxLength):
                if i < messageLength:
                    stateMatrix.append(format(ord(message[i]), "x"))
                else:
                    stateMatrix.append(format(ord(" "), "x"))

                if i < keyLength:
                    roundKey.append(format(ord(key[i]), "x"))
                else:
                    roundKey.append(format(ord(" "), "x"))

            
            self.roundkeys.insert(0,roundKey)
            print(self.roundkeys)

            #find all roundkeys for each round
            for i in range(1,11):
                roundKey = self.findRoundKey(roundKey,i-1)
                self.roundkeys.insert(i, roundKey)

     
        
            #round 0 add roundkey to message
            for i in range(0,maxLength):
                stateMatrix[i] = self.XOR(stateMatrix[i], self.roundkeys[0][i] , 16)

            #There are 10 rounds 
            for i in range(1,11):

                #Step 1: substitute bytes
                stateMatrix = self.substitution(stateMatrix, False)

                #Step 2: shift rows of matrix to the left      

                #shift 2nd row 1 time
                row = [stateMatrix[1] ,stateMatrix[5] ,stateMatrix[9] ,stateMatrix[13]]  
             
                stateMatrix[13] = row[0]
                stateMatrix[9] = row[3]
                stateMatrix[5]  = row[2]
                stateMatrix[1]  = row[1]

                #shift 3rd row 2 times 
                row = [stateMatrix[2] , stateMatrix[6] , stateMatrix[10] , stateMatrix[14] ] 
                stateMatrix[14] = row[1]
                stateMatrix[10] = row[0]
                stateMatrix[6]  = row[3]
                stateMatrix[2]  = row[2]
                
                #shift last row 3 times 
                row = [stateMatrix[3] , stateMatrix[7] , stateMatrix[11] , stateMatrix[15] ]         
                stateMatrix[15] = row[2]
                stateMatrix[11] = row[1]
                stateMatrix[7]  = row[0]
                stateMatrix[3]  = row[3]

                #step 3 Mix Columns
                if i != 10:
                    stateMatrix = self.mixColumns(fixedMatrix, [stateMatrix[0:4],stateMatrix[4:8] , stateMatrix[8:12] , stateMatrix[12:16] ] ) 
 
                #step 4 Add Round key
                for j in range(0, maxLength):
                    stateMatrix[j] = self.XOR(stateMatrix[j] , self.roundkeys[i][j] , 16)
                

        else:
            messagebox.showerror("KeyKryption Error", "Message must have 16 or less characters")

        for i in range(0,maxLength):
            if len(stateMatrix[i]) == 1:
                print('0' + stateMatrix[i], end=" ")
            else:
                print(stateMatrix[i], end=" ")
        

    def mixColumns(self, m1, m2):
        
        newState = []
        results = []  
        #multiply 4x4 matrix
        for i in range (0,4):
            for j in range(0,4):
                for k in range(0,4):
                    if m1[k][j] == "03":
                        results.append(self.XOR(hex((int("02",16) * int(m2[i][k] , 16))).split('x')[-1] , m2[i][k] , 16)) 
                    elif m1[k][j] == "09": #(((x * 2) * 2) * 2) + x
                        val = int("02",16) * int(m2[i][k],16)
                        reducedByte = self.reduceToByte(val) 
                        val = int(reducedByte,16) * int("02" , 16)
                        reducedByte = self.reduceToByte(val)
                        val = int(reducedByte,16) * int("02" , 16)
                        reducedByte = self.reduceToByte(val)
                        results.append(self.XOR(reducedByte, m2[i][k] , 16))  
                    elif m1[k][j] == "11": #((((x * 2) * 2) + x) * 2) + x
                        val = int("02",16) * int(m2[i][k],16)
                        reducedByte = self.reduceToByte(val) 
                        val = int(reducedByte,16) * int("02" , 16)
                        reducedByte = self.reduceToByte(val)
                        xorValue = self.XOR(reducedByte,m2[i][k],16)
                        val = int("02",16) * int(xorValue , 16) 
                        reducedByte = self.reduceToByte(val)
                        results.append(self.XOR(reducedByte, m2[i][k] , 16))
                    elif m1[k][j] == "13": #((((x * 2) + x) * 2) * 2) + x
                        val = int("02",16) * int(m2[i][k],16)
                        reducedByte = self.reduceToByte(val) 
                        xorValue = self.XOR(reducedByte,m2[i][k],16)
                        val = int("02",16) * int(xorValue , 16) 
                        reducedByte = self.reduceToByte(val)
                        val = int(reducedByte,16) * int("02" , 16)
                        reducedByte = self.reduceToByte(val)
                        results.append(self.XOR(reducedByte, m2[i][k] , 16))  
                    elif m1[k][j] == "14": #((((x * 2) + x) * 2) + x) * 2
                        val = int("02",16) * int(m2[i][k],16)
                        reducedByte = self.reduceToByte(val) 
                        xorValue = self.XOR(reducedByte,m2[i][k],16)
                        val = int("02",16) * int(xorValue , 16) 
                        reducedByte = self.reduceToByte(val)
                        xorValue = self.XOR(reducedByte,m2[i][k],16)
                        val = int("02",16) * int(xorValue , 16) 
                        reducedByte = self.reduceToByte(val)
                        results.append(reducedByte)
                    else:
                        results.append(hex((int(m1[k][j],16) * int(m2[i][k] , 16))).split('x')[-1])
            
                val1 = self.XOR(results[0], results[1] , 16)
                val2 = self.XOR(val1,results[2] , 16)
                val3 = self.XOR(val2, results[3] , 16)
            
                newState.append(val3)
                results.clear()

        return newState


    def substitution(self, m1, isInverse):
        
        row = 0
        column = 0
        m = []

        for i in range(0,len(m1)):
                
            #its possible for out of index error
            try:
                column = int(m1[i][1] , 16)
                row = int(m1[i][0], 16)
            except IndexError:
                column = int(m1[i][0], 16)
                row = 0

                
            if isInverse:
                m.append(self.InverseSBox[row][column])
            else:
                m.append(self.SBox[row][column])

        return m


    def decrypt(self):

        #set up variables
        w0 = []
        w1 = []
        w2 = []
        w3 = []
        roundKey = []
        stateMatrix = []
        inverseFixedMatrix = [["14","09" , "13" , "11"] , ["11" , "14" , "09" , "13"] , ["13", "11" , "14" , "09"] , ["09" , "13" , "11" , "14"]]
        maxMessageLength = 32
        maxKeyLength=16
        message = self.userInputTxt.get()
        key = "Thats my Kung Fu"
        keyLength = len(key)
        startIndex = 0
        maxMatrixLength = 16

         #get rid of the spaces
        noSpacesInMessage = message.replace(" ", "")
        messageLength = len(noSpacesInMessage)

        #decrypted message 
        if messageLength <= maxMessageLength:


            #turn key into hexadecimal
            for i in range(0,maxKeyLength):
                if i < keyLength:
                    roundKey.append(format(ord(key[i]), "x"))
                else:
                    roundKey.append(format(ord(" "), "x"))

           

            #make decrypted message a state matrix
            for endIndex in range(1,maxMessageLength+1):
                if endIndex % 2 == 0:
                    stateMatrix.append(noSpacesInMessage[startIndex:endIndex])
                    startIndex = startIndex+2


            self.roundkeys.insert(0,roundKey)
          
            #find all roundkeys for each round
            for i in range(1,11):
                roundKey = self.findRoundKey(roundKey,i-1)
                self.roundkeys.insert(i, roundKey)

            #round 10 add roundkey to message
            for i in range(0, maxMatrixLength):
                stateMatrix[i] = self.XOR(stateMatrix[i], self.roundkeys[10][i] , 16)
            
            #start at round 10
            for i in range(10,0,-1):
                
                #Step 1: shift rows of matrix to the right      

                #shift 2nd row 1 time
                row = [stateMatrix[1] ,stateMatrix[5] ,stateMatrix[9] ,stateMatrix[13]]  
             
                stateMatrix[13] = row[2]
                stateMatrix[9] = row[1]
                stateMatrix[5]  = row[0]
                stateMatrix[1]  = row[3]

                #shift 3rd row 2 times 
                row = [stateMatrix[2] , stateMatrix[6] , stateMatrix[10] , stateMatrix[14] ] 
                stateMatrix[14] = row[1]
                stateMatrix[10] = row[0]
                stateMatrix[6]  = row[3]
                stateMatrix[2]  = row[2]
                
                #shift last row 3 times 
                row = [stateMatrix[3] , stateMatrix[7] , stateMatrix[11] , stateMatrix[15] ]         
                stateMatrix[15] = row[0]
                stateMatrix[11] = row[3]
                stateMatrix[7]  = row[2]
                stateMatrix[3]  = row[1]
                       
                #Step 2: substitute bytes using inverse s-box
                stateMatrix = self.substitution(stateMatrix, True)

                #step 3 Add Round key
                for j in range(0, maxMatrixLength):
                    stateMatrix[j] = self.XOR(stateMatrix[j] , self.roundkeys[i-1][j] , 16)

                #Step 4 Inverse Mix Columns
                if i != 1:
                    stateMatrix = self.mixColumns(inverseFixedMatrix, [stateMatrix[0:4],stateMatrix[4:8] , stateMatrix[8:12] , stateMatrix[12:16] ] ) 
 
       


            message = ""

            #combine all the hexadecimal values into one variable
            for i in range(0, maxMatrixLength):
                message += stateMatrix[i]

            #turn hex message into plaintext
            print(bytearray.fromhex(message).decode())
             
            
                


root = tk.Tk()
root.title('KeyKryption')
root.geometry('300x200')
root.resizable(False, False)
app = Application(master=root)
app.mainloop()
