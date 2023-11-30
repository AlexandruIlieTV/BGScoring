// See https://aka.ms/new-console-template for more information
//Console.WriteLine("Hello, World!");
class Program
{
    static void Main(string[] args)
    {
        Player myPlayer = new Player();
        Console.WriteLine(myPlayer.playername);
        Console.WriteLine(myPlayer.score);
    }
}