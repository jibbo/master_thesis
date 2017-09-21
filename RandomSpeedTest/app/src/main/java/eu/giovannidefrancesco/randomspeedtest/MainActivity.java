package eu.giovannidefrancesco.randomspeedtest;

import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.TextView;

import java.security.SecureRandom;
import java.util.Locale;
import java.util.Random;

public class MainActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
    }

    public void randomClick(View v) {
        Random random = new Random();
        long time = System.currentTimeMillis();
        random.nextInt();
        time = System.currentTimeMillis() - time;
        publishResult(time);
    }

    public void secureRandClick(View v) {
        Random random = new SecureRandom();
        long time = System.currentTimeMillis();
        random.nextInt();
        time = System.currentTimeMillis() - time;
        publishResult(time);
    }

    private void publishResult(long time) {
//        String s = String.format(Locale.getDefault(), "It took: %d ms", time);
        String s = "It took: " + time + "ms";
        ((TextView) findViewById(R.id.textview)).setText(s);
    }
}
