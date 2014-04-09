import Tkinter as tk
from PIL import ImageTk, Image
class InputRandCode(tk.Frame):
    def SubmitRandCode(self):
        if len(self.input.get()) == 4 or len(self.input.get()) == 0:
            self.quit()

    def inputOnKey(self, event):
        if event.char == '\r':
            self.SubmitRandCode()
            
    def setImage(self, imgPath):
        img = Image.open(imgPath)
        img = img.resize((img.size[0] * 2, img.size[1] * 2))
        self.img = ImageTk.PhotoImage(img)
        self.imgLabel.config(image = self.img)

    def getRandCode(self):
        self.input.delete(0, tk.END)
        self.input.focus_set()
        self.mainloop()
        return self.input.get()
        
    def windowCancel(self):
        print "canceled"
        
    def createWidgets(self):
        self.imgLabel = tk.Label(self)
        self.imgLabel.pack(side = "left")
        self.input = tk.Entry(self)
        self.input.pack(side="left")
        
        self.submitBtn = tk.Button(self, text="OK", command=self.SubmitRandCode)
        self.submitBtn.pack(side="left") 
        self.input.bind("<Key>", self.inputOnKey)  
        


    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.pack()
        self.createWidgets()
        #self.root.protocol("WM_DELETE_WINDOW", self.windowCancel)

if __name__== "__main__":
    app = InputRandCode();
    app.setImage("/vagrant_data/login.jpg");
    print app.getRandCode()
    print app.getRandCode()
