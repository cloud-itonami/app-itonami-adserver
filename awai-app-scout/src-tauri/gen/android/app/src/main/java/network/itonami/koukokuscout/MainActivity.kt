package network.itonami.koukokuscout

import android.content.res.Configuration
import android.os.Bundle
import androidx.activity.enableEdgeToEdge
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.WindowInsetsControllerCompat
import kotlin.math.max

// System bars and display cutout as padding of the content view, so the page
// never draws under the status or navigation bar (AWAI-3430; same approach as
// awai-os apps/isekai AWAI-3216, apps/x402 AWAI-3284 and Hiring AWAI-3392).
class MainActivity : TauriActivity() {
  override fun onCreate(savedInstanceState: Bundle?) {
    enableEdgeToEdge()
    super.onCreate(savedInstanceState)
    val content = findViewById<android.view.View>(android.R.id.content)
    ViewCompat.setOnApplyWindowInsetsListener(content) { view, insets ->
      val bars = insets.getInsets(WindowInsetsCompat.Type.systemBars() or WindowInsetsCompat.Type.displayCutout())
      val ime = insets.getInsets(WindowInsetsCompat.Type.ime())
      view.setPadding(bars.left, bars.top, bars.right, max(bars.bottom, ime.bottom))
      insets
    }
    applySystemBarAppearance(resources.configuration)
    ViewCompat.requestApplyInsets(content)
  }

  // uiMode is in the manifest's configChanges, so a theme switch arrives here
  // instead of recreating the activity.
  override fun onConfigurationChanged(newConfig: Configuration) {
    super.onConfigurationChanged(newConfig)
    applySystemBarAppearance(newConfig)
  }

  // The bars are drawn over the decor view (edge-to-edge), so paint it with the
  // page's background (@awai/ui --awai-background: #ffffff light, #14110f dark)
  // and pick dark icons in light mode and light icons in dark mode.
  private fun applySystemBarAppearance(config: Configuration) {
    val light = (config.uiMode and Configuration.UI_MODE_NIGHT_MASK) != Configuration.UI_MODE_NIGHT_YES
    window.decorView.setBackgroundColor(if (light) 0xFFFFFFFF.toInt() else 0xFF14110F.toInt())
    // The 3-button navigation scrim is chosen when the activity starts and does
    // not follow a live theme switch; without this the decor colour shows through.
    if (android.os.Build.VERSION.SDK_INT >= 29) window.isNavigationBarContrastEnforced = false
    WindowInsetsControllerCompat(window, findViewById(android.R.id.content)).apply {
      isAppearanceLightStatusBars = light
      isAppearanceLightNavigationBars = light
    }
  }
}
